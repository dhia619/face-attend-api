
class PermissionCode:
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    EMPLOYEES_READ = "employees:read"
    EMPLOYEES_WRITE = "employees:write"
    ROLE_READ = "roles:read"
    ROLE_WRITE = "roles:write"
    PERMISSION_READ = "permissions:read"
    DEPARTMENT_READ = "departments:read"
    DEPARTMENT_WRITE = "departments:write"
    ATTENDANCE_READ = "attendance:read"
    ATTENDANCE_WRITE = "attendance:write"
    DEVICES_READ = "devices:read"
    DEVICES_WRITE = "devices:write"
    REPORTS_READ = "reports:read"
    SHIFTS_READ = "shifts:read"
    SHIFTS_WRITE = "shifts:write"

PERMISSION_META = {
    PermissionCode.USERS_READ:       "View admin users",
    PermissionCode.USERS_WRITE:      "Create and edit admin users",
    PermissionCode.EMPLOYEES_READ:   "View employees",
    PermissionCode.EMPLOYEES_WRITE:  "Create and edit employees",
    PermissionCode.DEPARTMENT_READ:  "View departments",
    PermissionCode.DEPARTMENT_WRITE: "Create and edit departments",
    PermissionCode.ROLE_READ:        "View roles",
    PermissionCode.ROLE_WRITE:       "Create and edit roles",
    PermissionCode.ATTENDANCE_READ:  "View attendance records",
    PermissionCode.ATTENDANCE_WRITE: "Edit and correct attendance records",
    PermissionCode.DEVICES_READ:     "View devices",
    PermissionCode.DEVICES_WRITE:    "Register and edit devices",
    PermissionCode.REPORTS_READ:     "View reports and dashboard",
    PermissionCode.SHIFTS_READ:      "View shifts",
    PermissionCode.SHIFTS_WRITE:     "Create and edit shifts"
}

class RoleName:
    SUPER_ADMIN = "super_admin"

class ErrorMessage:
    INSUFFICIENT_PERMISSION = "Insufficient permissions."
    MISSING_ROLE_NAME = "The role name is missing."
    ROLE_NAME_EXIST = "A role with that name already exists."
    ROLE_NOT_FOUND = "Role not found."
    ROLE_DELETE_ERROR = "Failed to delete role."
    PERMISSION_NOT_FOUND = "Permission not found."
    ROLE_PERMISSION_EXIST = "The role already has that permission."
    ROLE_CREATE_ERROR = "Failed to create role."
