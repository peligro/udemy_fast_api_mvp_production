from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from models.models import Usuario
from sqlmodel import Session
from database import get_session

from interfaces.interfaces import UsuarioResponse
from utilidades.utilidades import formatear_fecha

import os
from dotenv import load_dotenv
load_dotenv()

#esquema de seguridad
oauht2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauht2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= "No autorizado",
        headers = {"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
        user_id:int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    usuario = session.get(Usuario, user_id)
    if usuario is None:
        raise credentials_exception
    
    return UsuarioResponse(
        id = usuario.id,
        nombre = usuario.nombre,
        telefono = usuario.telefono,
        correo = usuario.correo,
        estado_id = usuario.estado_id,
        estado = usuario.estado.nombre,
        perfil_id = usuario.perfil_id,
        perfil = usuario.perfil.nombre,
        fecha = formatear_fecha(usuario.fecha)
    )
