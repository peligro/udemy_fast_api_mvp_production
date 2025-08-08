from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse

from database import get_session
from sqlmodel import Session, select
from models.models import Platos, Negocio, PlatosCategoria
from interfaces.interfaces import NegociosSlugResponse, PlatoResponse
from utilidades.utilidades import formatear_fecha

#dotenv
from dotenv import load_dotenv
load_dotenv()
import os


router = APIRouter(prefix="/carta-menu", tags=["Carta"])


@router.get("/{slug}", response_model=NegociosSlugResponse)
async def show(slug: str, session: Session=Depends(get_session)):
    dato = session.exec(
        select(Negocio).where(Negocio.slug==slug, Negocio.estado_id==1)
    ).first()
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el negocio por el slug y que esté activo)"
        )
    platos = session.exec(
        select(Platos).where(Platos.negocio_id==dato.id)
    ).all()

    #convertimos cada plato a PlatoResponse
    platos_response=[
        PlatoResponse(
            id=plato.id,
            nombre=plato.nombre,
            ingredientes=plato.ingredientes,
            precio=plato.precio,
            foto=(
                f"{os.getenv('AWS_BUCKET_URL')}{os.getenv('S3_BUCKET_NAME')}/archivos/{plato.foto}"
                if os.getenv('ENVIRONMENT')=='local'
                else f"https://{os.getenv('S3_BUCKET_NAME')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/archivos/{plato.foto}"
            ),
            platoscategoria=plato.platoscategoria.nombre if plato.platoscategoria else None
        ) for plato in platos
    ]
    if os.getenv('ENVIRONMENT')=="local":
        logo_url=f"{os.getenv('AWS_BUCKET_URL')}{os.getenv('S3_BUCKET_NAME')}/archivos/{dato.logo}"
    else:
        logo_url=f"https://{os.getenv('S3_BUCKET_NAME')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/archivos/{dato.logo}"
    resultado ={
        "id": dato.id,
        "nombre": dato.nombre,
        "logo": logo_url,
        "mapa": dato.mapa,
        "descripcion": dato.descripcion,
        "slug": dato.slug,
        "correo": dato.correo,
        "telefono": dato.telefono,
        "estado_id": dato.estado_id,
        "estado": dato.estado.nombre if dato.estado else None,
        "usuario_id": dato.usuario_id,
        "usuario": dato.usuario.nombre if dato.usuario else None,
        "categoria_id": dato.categoria_id,
        "categoria": dato.categoria.nombre if dato.categoria else None,
        "direccion": dato.direccion,
        "fecha": formatear_fecha(dato.fecha),
        "platos": platos_response
    }
    return resultado
    