from fastapi import APIRouter, Depends, HTTPException,BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from app.utils.security import create_access_token, verify_password, get_user, TOKEN_EXPIRE_MINUTES, get_current_active_user_with_roles, create_reset_token,verify_reset_token
from app.core.database import get_read_session,get_write_session
from pydantic import BaseModel
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from app.utils.email import send_email
from app.utils.security import get_password_hash
from pydantic.networks import EmailStr


def login_for_access_token(router: APIRouter):
    class LoginRequest(BaseModel):
        email: EmailStr
        password: str

    @router.post("/login")
    async def login_for_access_token(
        login_data: LoginRequest,
        session: AsyncSession = Depends(get_read_session)
    ):
        from app.api.auth.user.model import User
        try:
            # Fetch the user based on username
            result = await session.execute(select(User).where(User.email == login_data.email))
            user = result.scalar_one_or_none()
            if not user or not verify_password(login_data.password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Get the role of the user based on documentId (role_id)
            role_name = user.role.name if user.role else None
            if not role_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User role not found",
                )
            
            # Include only documentId in the token
            access_token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"documentId": user.documentId},  # Use documentId here
                expires_delta=access_token_expires
            )
            return {
                "access_token": access_token,
                "token_type": "bearer",  # Token type for HTTPBearer
                "message":f"Welcome {user.username}!",
            }        
        except SQLAlchemyError as e:
                error_message = str(e).split("\n")[1]
                raise HTTPException(status_code=400, detail=error_message)
        except ValueError:
                raise HTTPException(
                    status_code=400, detail="ID must be a valid integer.")
        except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))


def get_user_profile(router: APIRouter):
    @router.get("/my-profile")
    async def read_user_profile(
        session: AsyncSession = Depends(get_read_session),
        current_user=Depends(get_current_active_user_with_roles(["admin"]))
    ):
        user = await get_user(current_user.documentId, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user


def base_forgot_password(router: APIRouter):
    class ForgotPasswordRequest(BaseModel):
        email: str

    @router.post("/forgot-password")
    async def forgot_password(
        forgot_password_data: ForgotPasswordRequest,
        background_tasks: BackgroundTasks,
        session: AsyncSession = Depends(get_read_session)
        ):
        from app.api.auth.user.model import User
        try:
            # Fetch the user based on email
            result = await session.execute(select(User).where(User.email == forgot_password_data.email))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            print(user.email)
            reset_token = create_reset_token(user.email)
            print(reset_token)
            email_subject = "Password Reset Request"
            data = user
            token = reset_token
            await send_email(background_tasks,[user.email],email_subject,data,token)

            return {"message": "Password reset link sent to your email"}
        except SQLAlchemyError as e:
            error_message = str(e).split("\n")[1]
            raise HTTPException(status_code=400, detail=error_message)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


def base_reset_password(router: APIRouter):
    class ResetPasswordRequest(BaseModel):
        new_password: str

    @router.put("/reset-password")
    async def reset_password(
        reset_password_data: ResetPasswordRequest,
        token: str,
        session: AsyncSession = Depends(get_write_session)
    ):
        from app.api.auth.user.model import User
        try:
            # Verify the reset token and get email
            email = verify_reset_token(token)
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired reset token"
                )

            # Fetch the user by email
            result = await session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            # Update the user's password
            user.password = reset_password_data.new_password

            # Commit changes
            await session.commit()
            session.refresh(user)

            return {"message": "Password successfully updated"}
        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
