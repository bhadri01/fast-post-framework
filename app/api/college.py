from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page, add_pagination
from app.schemas.college import CollegeResponse, CollegeCreate, CollegeUpdate
from app.crud.college import college
from app.core.database import get_read_session, get_write_session
from typing import Optional
import json
from sqlalchemy.exc import SQLAlchemyError
from app.services.filtering import parse_filters
from app.models.college import College

router = APIRouter(tags=["Colleges"])

def parse_filter_query(filters: Optional[str]) -> Optional[dict]:
    if filters:
        try:
            return json.loads(filters)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid filter JSON")
    return None

@router.get("", response_model=Page[CollegeResponse])
async def read_colleges(
    filters: Optional[str] = Query(None),
    sort: Optional[str] = Query("id:asc"),
    session: AsyncSession = Depends(get_read_session)
):
    """
    Get a paginated and filtered list of colleges.
    """
    try:
        parsed_filters = parse_filter_query(filters)
        filter_expression = parse_filters(College, parsed_filters) if parsed_filters else None
        sort_field, sort_direction = sort.split(":")
        if sort_direction.lower() not in ["asc", "desc"]:
            raise HTTPException(status_code=400, detail="Invalid sort direction. Use 'asc' or 'desc'.")
        result = await college.get_all(session, filters=filter_expression, sort=(sort_field, sort_direction))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{college_id}", response_model=CollegeResponse)
async def read_college(college_id: int, session: AsyncSession = Depends(get_read_session)):
    """
    Get a single college by ID.
    """
    db_college = await college.get(session, id=college_id)
    if not db_college:
        raise HTTPException(status_code=404, detail="College not found")
    return db_college

@router.post("", response_model=CollegeResponse)
async def create_college(
    college_in: CollegeCreate, session: AsyncSession = Depends(get_write_session)
):
    """
    Create a new college.
    """
    try:
        return await college.create(session, obj_in=college_in)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/{college_id}", response_model=CollegeResponse)
async def update_college(
    college_id: int, college_in: CollegeUpdate, session: AsyncSession = Depends(get_write_session)
):
    """
    Update an existing college.
    """
    try:
        result = await college.update(session, id=college_id, obj_in=college_in)
        if not result["success"]:
            raise HTTPException(
                status_code=400 if "error" in result else 404,
                detail={"message": result["message"], "error": result.get("error")},
            )
        return result["data"]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Error updating college", "error": str(e)},
        )

@router.delete("/{college_id}", response_model=bool)
async def delete_college(college_id: int, session: AsyncSession = Depends(get_write_session)):
    """
    Delete a college by ID.
    """
    db_college = await college.get(session, id=college_id)
    if not db_college:
        raise HTTPException(status_code=404, detail="College not found")

    try:
        return await college.delete(session, id=college_id)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Add pagination routes
add_pagination(router)
