from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from slugify import slugify

from models.models import Categoria
from database import get_session
from sqlmodel import Session
from sqlalchemy import desc


from interfaces.interfaces import GenericInterface, UsuarioResponse
from .dto.categoria_dto import CategoriaDto
from utilidades.seguridad import get_current_user

router = APIRouter(prefix="/categoria", tags=["Categorías"])


@router.get("/", response_model=list[Categoria])
async def index(session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    datos = session.query(Categoria).order_by(desc(Categoria.id)).all()
    return datos


@router.get("/{id}", response_model=Categoria)
async def index(id: int, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Categoria, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible"
        )
    return dato


@router.post("/", response_model=GenericInterface)
async def create(dto: CategoriaDto, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validación antes de entra al try para que no se repita el nombre
    #select * from estado where nombre='dto.nombre'
    existe = session.query(Categoria).filter(Categoria.nombre==dto.nombre).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (Ya existe un registro con este nombre)"
        )
    #creamos un objeto de Categoría pasando también el slug
    data_db=Categoria(nombre=dto.nombre, slug=slugify(dto.nombre))
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


@router.put("/{id}", response_model=GenericInterface)
async def update(id: int, dto:CategoriaDto, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Categoria, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible"
        )
    try:
        dato.nombre= dto.nombre
        dato.slug = slugify(dto.nombre)

        session.commit()
        session.refresh(dato)
        
        return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"estado":"ok", "mensaje":"Se modifica el registro exitosamente"}
        )
    except Exception as e:
        session.rollback() #Revierte cualquier cambio pendiente
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (algo se rompió, ya sea la bd)"
        )


@router.delete("/{id}", response_model=GenericInterface)
async def destroy(id: int, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Categoria, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible"
        )
    try:
        session.delete(dato)
        session.commit()
        return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"estado":"ok", "mensaje":"Se elimina el registro exitosamente"}
        )
    except Exception as e:
        session.rollback() #Revierte cualquier cambio pendiente
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (algo se rompió, ya sea la bd)"
        )