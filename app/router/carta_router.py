from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from sqlalchemy import desc

from utilidades.utilidades import formatear_fecha

from dotenv import load_dotenv
load_dotenv()
import os

from database import get_session
from interfaces.interfaces import  NegocioSlugResponse, PlatoResponse
from models.models import Negocio, Platos


router = APIRouter(prefix="/carta-menu", tags=["Carta"])


@router.get("/{slug}", response_model=NegocioSlugResponse)
async def show(slug: str, session: Session = Depends(get_session)):
    dato = session.exec(
        select(Negocio).where(Negocio.slug == slug, Negocio.estado_id == 1)
    ).first()

    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible (No existe negocio por slug)"
        )

    platos = session.exec(
        select(Platos).order_by(desc(Platos.id)).where(Platos.negocio_id == dato.id)
    ).all()

    # Convertimos cada Plato a PlatoResponse
    platos_response = [
        PlatoResponse(
            id=plato.id,
            nombre=plato.nombre,
            ingredientes=plato.ingredientes,
            precio=plato.precio,
            foto=f"{os.getenv('AWS_BUCKET_URL')}{os.getenv('S3_BUCKET_NAME')}/archivos/{plato.foto}",
            platoscategoria=plato.platoscategoria.nombre if plato.platoscategoria else None
        ) for plato in platos
    ]

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
        "estado": dato.estado.nombre if dato.estado else None,
        "usuario_id": dato.usuario_id,
        "usuario": dato.usuario.nombre if dato.usuario else None,
        "categoria_id": dato.categoria_id,
        "categoria": dato.categoria.nombre if dato.categoria else None,
        "direccion": dato.direccion,
        "fecha": formatear_fecha(dato.fecha),
        "platos": platos_response  # ✅ Ya es una lista de PlatoResponse
    }

    return resultado




