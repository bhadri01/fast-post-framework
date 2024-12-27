from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"
    TEACHER = "teacher"
    STAFF = "staff"
