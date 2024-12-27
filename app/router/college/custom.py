from fastapi import APIRouter

def add_custom_college_routes(router: APIRouter):
    @router.get("/custom", tags=["College"])
    async def custom_route():
        return {"message": "This is a custom route for the College model"}

