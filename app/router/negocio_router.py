from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse


from slugify import slugify

from models.models import Negocio, Categoria, Usuario, Estado
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


router = APIRouter(prefix="/negocio", tags=["Negocios"])



@router.get("/", response_model=list[NegocioInterface])
async def index(session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    datos = session.query(Negocio).order_by(desc(Negocio.id)).all()
    
    resultado = [
        NegocioInterface(
            id = dato.id,
            nombre= dato.nombre,
            logo=(
                f"{os.getenv('AWS_BUCKET_URL')}{os.getenv('S3_BUCKET_NAME')}/archivos/{dato.logo}"
                if os.getenv('ENVIRONMENT')=='local'
                else f"https://{os.getenv('S3_BUCKET_NAME')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/archivos/{dato.logo}"
            ),
            mapa= dato.mapa,
            descripcion=dato.descripcion, 
            slug = dato.slug,
            correo = dato.correo,
            telefono = dato.telefono,
            estado_id = dato.estado_id,
            estado = dato.estado.nombre if dato.estado else None,
            usuario_id = dato.usuario_id,
            usuario = dato.usuario.nombre  if dato.usuario else None,
            categoria_id = dato.categoria_id,
            categoria = dato.categoria.nombre if dato.categoria else None,
            direccion = dato.direccion,
            fecha = formatear_fecha(dato.fecha)
        ) for dato in datos
    ]
    
    return resultado

"""
@router.get("/", response_model=list[Negocio])
async def index(session: Session=Depends(get_session)):
    datos = session.query(Negocio).order_by(desc(Negocio.id)).all()
    
    resultado = [
        NegocioInterface(
            id = dato.id,
            nombre= dato.nombre,
            logo="",
            mapa= dato.mapa,
            descripcion=dato.descripcion, 
            slug = dato.slug,
            correo = dato.correo,
            telefono = dato.telefono,
            estado_id = dato.estado_id,
            estado = dato.estado.nombre,
            usuario_id = dato.usuario_id,
            usuario = dato.usuario.nombre,
            categoria_id = dato.categoria_id,
            categoria = dato.categoria.nombre,
            direccion = dato.direccion,
            #fecha = formatear_fecha(dato.fecha)
        ) for dato in datos
    ]
    
    return resultado
"""


"""
@router.get("/", response_model=list[Negocio])
async def index(session: Session=Depends(get_session)):
    datos = session.query(Negocio).order_by(desc(Negocio.id)).all()
    return datos
"""


@router.get("/{id}", response_model=NegocioInterface)
async def show(id: int, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Negocio, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no disponible"
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


"""
@router.post("/", response_model=GenericInterface)
async def create(dto: NegocioDto, session: Session=Depends(get_session)):
    data_db=Negocio(
        estado_id=1,
        usuario_id=dto.usuario_id,
        categoria_id=dto.categoria_id,
        nombre=dto.nombre, 
        slug=slugify(dto.nombre),
        correo=dto.correo,
        telefono=dto.telefono,
        direccion=dto.direccion,
        mapa=dto.mapa,
        descripcion=dto.descripcion,
        logo=os.getenv('S3_LOGO_NEGOCIO')
        )
    session.add(data_db)
    session.commit()
    session.refresh(data_db)
        
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"estado":"ok", "mensaje":"Se crea el registro exitosamente"}
        )
""" 

@router.post("/", response_model=GenericInterface)
async def create(dto: NegocioDto, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validamos si existe categoría
    categoria = session.get(Categoria, dto.categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe la categoría)"
        )
    
    #validamos si existe usuario
    #select * from usuario where id=dto.id and estado_id=dto.estado_id
    usuario = session.exec(
        select(Usuario).where(Usuario.id==dto.usuario_id, Usuario.estado_id==1)
    ).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el usuario)"
        )
    
    #validación antes de entra al try para que no se repita el nombre
    #select * from negocio where nombre='dto.nombre'
    existe = session.query(Negocio).filter(Negocio.nombre==dto.nombre).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (Ya existe un registro con este nombre)"
        )
    #creamos un objeto de Negocio pasando también el slug
    data_db=Negocio(
        estado_id=1,
        usuario_id=dto.usuario_id,
        categoria_id=dto.categoria_id,
        nombre=dto.nombre, 
        slug=slugify(dto.nombre),
        correo=dto.correo,
        telefono=dto.telefono,
        direccion=dto.direccion,
        mapa=dto.mapa,
        descripcion=dto.descripcion,
        logo=os.getenv('S3_LOGO_NEGOCIO')
        )
    #se crea el registro
    try:
        session.add(data_db)
        session.commit()
        session.refresh(data_db)
        
        return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"estado":"ok", "mensaje":"Se crea el registro exitosamente"}
        )
    except:
        session.rollback() #Revierte cualquier cambio pendiente
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (algo se rompió, ya sea la bd)"
        )


@router.put("/{id}", response_model=NegocioInterface)
async def update(id: int, dto: NegocioDto, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validamos si existe categoría
    categoria = session.get(Categoria, dto.categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe la categoría)"
        )
    #validamos si existe estado
    estado = session.get(Estado, dto.estado_id)
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el estado)"
        )
    #validamos si existe usuario
    #select * from usuario where id=dto.id and estado_id=dto.estado_id
    usuario = session.exec(
        select(Usuario).where(Usuario.id==dto.usuario_id, Usuario.estado_id==1)
    ).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el usuario)"
        )
    dato = session.get(Negocio, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no disponible"
        )
    try:
        dato.nombre= dto.nombre
        dato.slug = slugify(dto.nombre)
        dato.categoria_id = dto.categoria_id
        dato.usuario_id = dto.usuario_id
        dato.estado_id = dto.estado_id
        dato.correo = dto.correo
        dato.telefono = dto.telefono
        dato.direccion = dto.direccion
        dato.mapa = dto.mapa
        dato.descripcion = dto.descripcion

        session.commit()
        session.refresh(dato)
        return JSONResponse(
            status_code = status.HTTP_200_OK,
            content = {"estado":"ok", "mensaje":"Se modifica el registro exitosamente"}
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (se rompió la bd)"
        )


@router.delete("/{id}", response_model=NegocioInterface)
async def destroy(id: int, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Negocio, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no disponible"
        )
    try:
        session.delete(dato)
        session.commit()
        return JSONResponse(
            status_code = status.HTTP_200_OK,
            content = {"estado":"ok", "mensaje":"Se elimina el registro exitosamente"}
        )
    except Exception as e:
        session.rollback()