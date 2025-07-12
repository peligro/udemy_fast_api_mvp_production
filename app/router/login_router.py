from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()


from database import get_session
from interfaces.interfaces import GenericInterface, LoginResponse
from models.models import Usuario
from .dto.login_dto import LoginDto
from utilidades.utilidades import verify_password, create_access_token


router = APIRouter(prefix="/auth/login", tags=["Login"])


@router.post("/", response_model=LoginResponse)
async def login(dto: LoginDto, session: Session = Depends(get_session)):
    # Buscar al usuario por correo
    dato = dato = session.exec(
        select(Usuario).where(Usuario.correo == dto.correo, Usuario.estado_id == 1)
    ).first()

    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (No existe el correo)"
        )

    # Verificar la contraseña
    if not verify_password(dto.password, dato.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (Contraseña incorrecta)"
        )
    token = create_access_token(
        data={
            "sub": str(dato.id),
            "nombre": dato.nombre,
            "issuer":os.getenv('ISSUER')
        }
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "estado": "ok",
            "mensaje": "Inicio de sesión exitoso",
            "data": {
                "id": dato.id,
                "nombre": dato.nombre,
                "perfil_id":dato.perfil_id,
                "token": token
            }
        }
    )