import asyncio
import base64
import threading
from typing import Dict

import cv2
import httpx
from sqlalchemy import select

from src.database import db_session
from src.config import get_settings
from src.devices.models import Device
from src.devices.constants import DeviceStatus, DeviceType


settings = get_settings()

RECOGNITION_URL = (
    settings.BASE_URL
    + settings.BASE_API_PATH
    + "/recognition/ip-camera"
)

DB_REFRESH_INTERVAL = 10
CAPTURE_INTERVAL = 0.5
RECONNECT_DELAY = 5


class LatestFrameCapture:
    """
    Continuously drains the RTSP stream in a dedicated thread
    and keeps only the newest frame.

    This prevents old frames from building up while the
    recognition API is processing previous frames.
    """

    def __init__(self, rtsp_url: str):
        self.rtsp_url = rtsp_url

        self.cap = None
        self.frame = None

        self.frame_lock = threading.Lock()

        self.running = False
        self.thread = None

    def start(self) -> bool:
        """
        Open the RTSP stream and start the reader thread.
        """

        self.stop()

        self.cap = cv2.VideoCapture(
            self.rtsp_url,
            cv2.CAP_FFMPEG,
        )

        self.cap.set(
            cv2.CAP_PROP_BUFFERSIZE,
            1,
        )

        if not self.cap.isOpened():
            self.cap.release()
            self.cap = None
            return False

        self.running = True

        self.thread = threading.Thread(
            target=self._reader_loop,
            daemon=True,
        )

        self.thread.start()

        return True

    def _reader_loop(self):
        """
        Continuously read the RTSP stream.

        Each new frame replaces the previous one.
        Frames are never queued.
        """

        while (
            self.running
            and self.cap is not None
        ):
            success, frame = self.cap.read()

            if not success or frame is None:
                self.running = False
                break

            with self.frame_lock:
                self.frame = frame

    def read_latest(self):
        """
        Return a copy of the latest available frame.
        """

        with self.frame_lock:
            if self.frame is None:
                return None

            return self.frame.copy()

    def is_running(self) -> bool:
        return (
            self.running
            and self.cap is not None
            and self.cap.isOpened()
        )

    def stop(self):
        """
        Stop RTSP reader and release resources.
        """

        self.running = False

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        if (
            self.thread is not None
            and self.thread.is_alive()
            and self.thread
            is not threading.current_thread()
        ):
            self.thread.join(timeout=1.0)

        self.thread = None

        with self.frame_lock:
            self.frame = None


class CameraWorker:
    def __init__(self):
        self.camera_tasks: Dict[
            int,
            asyncio.Task
        ] = {}

        self.http_client = httpx.AsyncClient(
            timeout=15.0
        )

    async def run(self):
        print("[WORKER] Camera worker started")
        try:
            while True:
                try:
                    await self.sync_cameras()
                except Exception as e:
                    print("[WORKER] "f"Error while syncing cameras: {e}")
                await asyncio.sleep(DB_REFRESH_INTERVAL)
        finally:
            await self.shutdown()

    async def sync_cameras(self):
        """
        Read active IP cameras from DB.

        - Start newly added cameras
        - Stop deleted/disabled cameras
        """

        async with db_session() as db:
            result = await db.execute(
                select(Device)
                .where(
                    Device.type == DeviceType.IP_CAMERA.value,
                    Device.status == DeviceStatus.ACTIVE.value,
                )
            )

            cameras = result.scalars().all()

        active_camera_ids = {camera.id for camera in cameras}

        for camera in cameras:
            if camera.id in self.camera_tasks:
                continue
            if not camera.rtsp_url:
                print(f"[CAMERA {camera.id}] No RTSP URL configured")
                continue

            print(f"[WORKER] Starting camera {camera.id} - {camera.name}")

            task = asyncio.create_task(
                self.camera_loop(
                    camera_id=camera.id,
                    rtsp_url=camera.rtsp_url,
                )
            )

            self.camera_tasks[camera.id] = task

        for camera_id in list(self.camera_tasks.keys()):
            if camera_id in active_camera_ids:
                continue

            print(f"[WORKER] Stopping camera {camera_id}")

            task = self.camera_tasks.pop(camera_id)
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass

    async def camera_loop(
        self,
        camera_id: int,
        rtsp_url: str,
    ):
        """
        Continuously consume RTSP frames.

        A background reader keeps replacing
        the current frame with the newest one.

        Every CAPTURE_INTERVAL seconds,
        the latest frame is sent for recognition.
        """

        stream = None

        print(f"[CAMERA {camera_id}] Starting RTSP loop")

        try:
            while True:
                if (stream is None or not stream.is_running()):
                    if stream is not None:
                        stream.stop()

                    print(f"[CAMERA {camera_id}] Connecting to RTSP...")

                    stream = LatestFrameCapture(rtsp_url)
                    connected = await asyncio.to_thread(stream.start)

                    if not connected:
                        print(
                            f"[CAMERA {camera_id}] "
                            "Unable to connect. "
                            f"Retrying in "
                            f"{RECONNECT_DELAY}s..."
                        )

                        stream.stop()
                        stream = None

                        await asyncio.sleep(RECONNECT_DELAY)

                        continue

                    print(f"[CAMERA {camera_id}] Connected successfully")

                    await asyncio.sleep(0.1)

                frame = stream.read_latest()

                if frame is None:
                    if not stream.is_running():
                        print(
                            f"[CAMERA {camera_id}] "
                            "RTSP reader stopped. "
                            "Reconnecting..."
                        )

                        stream.stop()
                        stream = None

                        await asyncio.sleep(RECONNECT_DELAY)
                    else:
                        await asyncio.sleep(0.05)
                    continue

                await self.send_frame(
                    camera_id=camera_id,
                    frame=frame,
                )

                await asyncio.sleep(CAPTURE_INTERVAL)

        except asyncio.CancelledError:
            print(f"[CAMERA {camera_id}] Task cancelled")
            raise

        except Exception as e:
            print(f"[CAMERA {camera_id}] Unexpected error: {e}")

        finally:
            if stream is not None:
                stream.stop()

            print(f"[CAMERA {camera_id}] RTSP stream closed")

    async def send_frame(
        self,
        camera_id: int,
        frame,
    ):
        """
        Convert frame to JPEG then to Base64
        and send to recognition API.
        """

        success, buffer = cv2.imencode(
            ".jpg",
            frame,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                85,
            ],
        )

        if not success:
            print(f"[CAMERA {camera_id}] Failed to encode JPEG")
            return

        image_bytes = buffer.tobytes()

        face_image_base64 = (
            "data:image/jpeg;base64,"
            + base64.b64encode(
                image_bytes
            ).decode("utf-8")
        )

        payload = {
            "face_image": face_image_base64,
            "device_id": camera_id,
        }

        try:
            response = await self.http_client.post(
                RECOGNITION_URL,
                json=payload,
            )
            if response.is_success:
                try:
                    result = response.json()
                except Exception:
                    result = None
                if (isinstance(result, dict) and result.get("full_name")):
                    print(
                        f"[CAMERA {camera_id}] "
                        f"{result.get('full_name')} "
                        f"{'has done ' if result.get("already_recorded") == True else 'is doing '}"
                        f"{result.get('check_type')} "
                        f"at "
                        f"{result.get('timestamp')}"
                    )
            else:
                print(
                    f"[CAMERA {camera_id}] "
                    "Recognition failed "
                    f"[{response.status_code}]: "
                    f"{response.text}"
                )

        except httpx.RequestError as e:
            print(f"[CAMERA {camera_id}] Recognition API unavailable: {e}")

        except Exception as e:
            print(f"[CAMERA {camera_id}] Error sending frame :{e}")

    async def shutdown(self):
        print("[WORKER] Shutting down...")

        for (camera_id, task) in self.camera_tasks.items():
            print(f"[WORKER] Stopping camera {camera_id}")
            task.cancel()

        if self.camera_tasks:

            await asyncio.gather(
                *self.camera_tasks.values(),
                return_exceptions=True,
            )

        self.camera_tasks.clear()

        await self.http_client.aclose()

        print("[WORKER] Shutdown complete")


async def main():
    worker = CameraWorker()

    try:
        await worker.run()

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())