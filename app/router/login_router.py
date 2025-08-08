from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse


from database import get_session
from sqlmodel import Session, select
from .dto.login_dto import LoginDto
from interfaces.interfaces import LoginResponse, GenericInterface
from utilidades.utilidades import verify_password, create_access_token
from models.models import  Usuario

import os 
from dotenv import load_dotenv
load_dotenv()


router = APIRouter(prefix="/auth/login", tags=["Login"])


@router.post("/", response_model=LoginResponse )
async def login(dto: LoginDto, session: Session=Depends(get_session)):
    #paso 1: verificación del correo y usuario activo
    dato = session.exec(
        select(Usuario).where(Usuario.correo==dto.correo, Usuario.estado_id==1)
    ).first()
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el correo)"
        )
    #paso 2: verificación del password
    if not verify_password(dto.password, dato.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (Contraseña incorrecta)"
        )
    #paso 3: generar token JWT
    token = create_access_token(
        data={
            "sub": str(dato.id),
            "nombre": dato.nombre,
            "issuer": os.getenv('ISSUER')
        }
    )
    #paso 4: retornamos todo
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "estado":"ok",
            "mensaje":"Inicio de sesión exitoso",
            "data":{
                "id": dato.id,
                "nombre": dato.nombre,
                "perfil_id": dato.perfil_id,
                "token": token
            }
        }
    )
    
    