from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session
from sqlalchemy import desc
from slugify import slugify
from utilidades.utilidades import formatear_fecha
from utilidades.seguridad import get_current_user

from dotenv import load_dotenv
load_dotenv()
import os

from database import get_session
from interfaces.interfaces import NegocioResponse, UsuarioResponse
from models.models import Negocio, Usuario
from .dto.negocio_dto import NegocioDto


router = APIRouter(prefix="/negocio-por-usuario", tags=["Negocio por Usuario"])





@router.get("/{id}", response_model=NegocioResponse)
async def show(id: int, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validamos si existe usuario
    usuario = session.get(Usuario, id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el usuario)"
        )
    dato = session.query(Negocio).filter(Negocio.usuario_id == id).first()
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"estado": "error", "mensaje": "Recurso no disponible"}
        )
    resultado = {
        "id": dato.id,
        "nombre": dato.nombre,
        "logo": f"{os.getenv('AWS_BUCKET_URL')}{os.getenv('S3_BUCKET_NAME')}/archivos/{dato.logo}",
        "mapa": dato.mapa,
        "facebook": dato.facebook,
        "descripcion": dato.descripcion,
        "instagram": dato.instagram,
        "twitter": dato.twitter,
        "slug": dato.slug,
        "correo": dato.correo,
        "tiktok": dato.tiktok,
        "telefono": dato.telefono,
        "estado_id": dato.estado_id,
        "estado": dato.estado.nombre,
        "usuario_id": dato.usuario_id,
        "usuario": dato.usuario.nombre,
        "categoria_id": dato.categoria_id,
        "categoria": dato.categoria.nombre,
        "direccion": dato.direccion,
        "fecha": formatear_fecha(dato.fecha)
    }

    return resultado

