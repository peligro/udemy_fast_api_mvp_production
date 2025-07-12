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
from interfaces.interfaces import GenericInterface, NegocioResponse, UsuarioResponse
from models.models import Negocio, Categoria, Estado, Usuario
from .dto.negocio_dto import NegocioDto


router = APIRouter(prefix="/negocio", tags=["Negocios"])

@router.get("/", response_model=list[NegocioResponse])
async def index(session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    datos = session.query(Negocio).order_by(desc(Negocio.id)).all()
    
    resultado = [
        NegocioResponse(
            id=dato.id,
            nombre=dato.nombre,
            logo=f"{os.getenv('AWS_BUCKET_URL')}{os.getenv('S3_BUCKET_NAME')}/archivos/{dato.logo}",
            mapa=dato.mapa,
            facebook=dato.facebook,
            descripcion=dato.descripcion,
            instagram=dato.instagram,
            twitter=dato.twitter,
            slug=dato.slug,
            correo=dato.correo,
            tiktok=dato.tiktok,
            telefono=dato.telefono,
            estado_id=dato.estado_id,
            estado=dato.estado.nombre if dato.estado else None,
            usuario_id=dato.usuario_id,
            usuario=dato.usuario.nombre if dato.usuario else None,
            categoria_id=dato.categoria_id,
            categoria=dato.categoria.nombre if dato.categoria else None,
            direccion=dato.direccion,
            fecha=formatear_fecha(dato.fecha)
        ) for dato in datos
    ]
    
    return resultado



@router.get("/{id}", response_model=NegocioResponse)
async def show(id: int, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Negocio, id)
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

"""
@router.get("/{id}", response_model=Negocio)
async def show(id: int, session: Session = Depends(get_session)):
    dato = session.get(Negocio, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Recurso no disponible"}
        )
    return dato
"""


@router.post("/", response_model=GenericInterface)
async def create(dto: NegocioDto, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validamos si existe categoría
    categoria = session.get(Categoria, dto.categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe la categoría)"
        )
    #validamos si existe usuario
    usuario = session.get(Usuario, dto.usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el usuario)"
        )
    # Validación: nombre duplicado
    existe = session.query(Negocio).filter(Negocio.nombre == dto.nombre).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un registro con ese nombre"
        )
    dato_db = Negocio(
        estado_id=1,
        usuario_id=dto.usuario_id,
        categoria_id=dto.categoria_id,
        nombre=dto.nombre, 
        slug=slugify(dto.nombre),
        correo=dto.correo,
        telefono=dto.telefono,
        direccion=dto.direccion,
        logo="94972b65-2bca-4804-b3dd-7ce927320be4.jpg",
        facebook=dto.facebook,
        instagram=dto.instagram,
        twitter=dto.twitter,
        tiktok=dto.tiktok,
        mapa=dto.mapa,
        descripcion=dto.descripcion
        )
    try:
        session.rollback()
        session.add(dato_db)
        session.commit()
        session.refresh(dato_db)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"estado": "ok", "mensaje": "Se crea el registro exitosamente"},
        )

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Ocurrió un error al crear el registro", "detalle": str(e)}
        )


@router.put("/{id}", response_model=GenericInterface)
async def update(id: int, dto: NegocioDto, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validamos si existe categoría
    categoria = session.get(Categoria, dto.categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe la categoría)"
        )
    #validamos si existe usuario
    usuario = session.get(Usuario, dto.usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el usuario)"
        )
    #validamos si existe estado
    estado = session.get(Estado, dto.estado_id)
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el estado)"
        )
    dato = session.get(Negocio, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Recurso no disponible"}
        )
    try:
        dato.nombre = dto.nombre
        dato.slug = slugify(dto.nombre)
        dato.categoria_id=dto.categoria_id
        dato.estado_id=dto.estado_id
        dato.usuario_id=dto.usuario_id
        dato.correo=dto.correo
        dato.telefono=dto.telefono
        dato.direccion=dto.direccion
        dato.facebook=dto.facebook
        dato.twitter=dto.twitter
        dato.instagram=dto.instagram
        dato.mapa=dto.mapa,
        dato.descripcion=dto.descripcion
        session.commit()
        session.refresh(dato)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content= {"estado": "ok", "mensaje": f"Se modifica el registro exitosamente"},
        )
    except Exception as e:
        session.rollback()  # Revierte cualquier cambio pendiente
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Ocurrió un error inesperado" }
        )


@router.delete("/{id}", response_model=GenericInterface)
async def destroy(id: int, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Negocio, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible"
        )
    try:
        session.delete(dato)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content= {"estado": "ok", "mensaje": f"Se elimina el registro exitosamente"},
    )  





