from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse


from slugify import slugify

from models.models import Negocio, Usuario
from database import get_session
from sqlmodel import Session, select
from sqlalchemy import desc
import uuid

from interfaces.interfaces import GenericInterface, NegocioInterface, UsuarioResponse
from .dto.negocio_dto import NegocioDto
from utilidades.utilidades import formatear_fecha
from utilidades.seguridad import get_current_user


#dotenv
from dotenv import load_dotenv
load_dotenv()
import os


router = APIRouter(prefix="/negocio-por-usuario", tags=["Negocio por Usuario"])




@router.get("/{id}", response_model=NegocioInterface)
async def show(id: int, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validamos si existe el usuario
    usuario = session.get(Usuario, id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (usuario no existe)"
        )

    dato = session.query(Negocio).filter(Negocio.usuario_id==id).first()
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (No hay negocio asociado al usuario)"
        )
    if os.getenv('ENVIRONMENT')=="local":
        logo_url=f"{os.getenv('AWS_BUCKET_URL')}{os.getenv('S3_BUCKET_NAME')}/archivos/{dato.logo}"
    else:
        logo_url=f"https://{os.getenv('S3_BUCKET_NAME')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/archivos/{dato.logo}"
    resultado = {
        "id": dato.id,
        "nombre": dato.nombre,
        "logo":logo_url,
        "mapa": dato.mapa,
        "descripcion":dato.descripcion, 
        "slug" : dato.slug,
        "correo" : dato.correo,
        "telefono" : dato.telefono,
        "estado_id" : dato.estado_id,
        "estado" : dato.estado.nombre if dato.estado else None,
        "usuario_id" : dato.usuario_id,
        "usuario" : dato.usuario.nombre  if dato.usuario else None,
        "categoria_id" : dato.categoria_id,
        "categoria" : dato.categoria.nombre if dato.categoria else None,
        "direccion" : dato.direccion,
        "fecha" : formatear_fecha(dato.fecha)
    }
    return resultado


