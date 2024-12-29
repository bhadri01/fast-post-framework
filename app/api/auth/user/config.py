from .routes import login_for_access_token, get_user_profile,base_reset_password,base_forgot_password

user = {
    "required_roles": {
        "read_all": ["admin"],
        "read_one": ["admin"],
        "create": ["admin"],
        "update": ["admin"],
        "delete": ["admin"]
    },
    "custom_routes": [
        login_for_access_token,
        get_user_profile,
        base_reset_password,
        base_forgot_password

    ]
}
