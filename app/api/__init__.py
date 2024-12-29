"""
This module initializes the API by importing the necessary models and their configurations.
"""

# Import models

from app.api.auth.user.model import User
from app.api.auth.role.model import Role

# Import model configurations
from app.api.auth.user.config import user
from app.api.auth.role.config import role

model_configs = {
    "User": user,
    "Role": role,
}