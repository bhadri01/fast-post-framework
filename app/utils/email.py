from pydantic import BaseModel, EmailStr
from typing import List
from fastapi import HTTPException, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os

class EmailSchema(BaseModel):
    email: List[EmailStr]

# Ensure the template folder path is correct
template_folder_path = os.path.join(os.path.dirname(__file__), 'templates') 

conf = ConnectionConfig(
    MAIL_USERNAME="admin@succeedex.in",
    MAIL_PASSWORD="Dotmail@1234",
    MAIL_FROM="admin@succeedex.in",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.hostinger.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    MAIL_FROM_NAME="Succeedex",
    TEMPLATE_FOLDER=template_folder_path
)

async def send_email(background_tasks: BackgroundTasks, email: List[str], subject: str, body: str,token:str):
    try:
        message = MessageSchema(
            subject=subject,
            recipients=email,  # Ensure recipients is a list
            template_body={"token":token,"username":body.username},  # Ensure body is a string
            subtype="html"
        )
        
        fm = FastMail(conf)
        background_tasks.add_task(
            fm.send_message, message, template_name='email.html')
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))