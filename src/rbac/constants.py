
class PermissionCode:
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    EMPLOYEES_READ = "employees:read"
    EMPLOYEES_WRITE = "employees:write"
    ATTENDANCE_READ = "attendance:read"
    ATTENDANCE_WRITE = "attendance:write"
    DEVICES_READ = "devices:read"
    DEVICES_WRITE = "devices:write"
    REPORTS_READ = "reports:read"

PERMISSION_META = {
    PermissionCode.USERS_READ:       "View admin users",
    PermissionCode.USERS_WRITE:      "Create and edit admin users",
    PermissionCode.EMPLOYEES_READ:   "View employees",
    PermissionCode.EMPLOYEES_WRITE:  "Create and edit employees",
    PermissionCode.ATTENDANCE_READ:  "View attendance records",
    PermissionCode.ATTENDANCE_WRITE: "Edit and correct attendance records",
    PermissionCode.DEVICES_READ:     "View devices",
    PermissionCode.DEVICES_WRITE:    "Register and edit devices",
    PermissionCode.REPORTS_READ:     "View reports and dashboard",
}

class RoleName:
    SUPER_ADMIN = "super_admin"
