import logging

from httpx import (
    AsyncClient,
    HTTPStatusError,
    TimeoutException,
    ConnectError,
)

from src.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


async def get_face_embedding(face_image: str) -> list | None:
    async with AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.DEEPFACE_API_URL}/represent",
                json={
                    "img": face_image,
                    "model_name": settings.FACE_EMBEDDING_MODEL,
                    "detector_backend": settings.FACE_DETECTOR_MODEL,
                    "enforce_detection": True,
                },
                timeout=10.0,
            )

            response.raise_for_status()

            data = response.json()
            return data["results"][0]["embedding"]

        except ConnectError:
            logger.error("Could not connect to DeepFace API")
            return None

        except TimeoutException:
            logger.error("DeepFace API timed out")
            return None

        except HTTPStatusError as e:
            logger.error(
                "DeepFace API error: %s",
                e.response.status_code,
            )
            return None

        except (KeyError, IndexError):
            logger.warning("Invalid DeepFace response or no face detected")
            return None