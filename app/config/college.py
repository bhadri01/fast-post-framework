from app.router.college.custom import add_custom_college_routes

college_config = {
    "required_roles": {
        "read_all": [],
        "read_one": [],
        "create": [],
        "update": [],
        "delete": []
    },
    "custom_routes": [
        add_custom_college_routes
    ]
}
