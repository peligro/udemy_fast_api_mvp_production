from datetime import datetime, timedelta
import bcrypt
from typing import Optional
from fastapi import status, HTTPException

from jose import jwt, JWTError

import os
from dotenv import load_dotenv
load_dotenv()

#email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def formatear_fecha(fecha: datetime) -> str:
    return fecha.strftime("%d/%m/%Y")


def generate_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict, expires_delta: Optional[timedelta]=None):
    to_encode = data.copy()
    expipe_minutos = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', "30"))
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=expipe_minutos))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))


def decode_access_token(token: str):
    try:
        return jwt.decode(token, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= "No autorizado",
            headers = {"WWW-Authenticate": "Bearer"}
        )



def sendMail(html, asunto, para):
    msg = MIMEMultipart('alternave')
    msg['Subject']= asunto
    msg['From'] = os.getenv('SMTP_USER')
    msg['To'] = para

    msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT'))
    server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
    server.sendmail(os.getenv('SMTP_USER'), para, msg.as_string())
    server.quit()


