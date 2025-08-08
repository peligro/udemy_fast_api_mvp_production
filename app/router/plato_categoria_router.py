from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from slugify import slugify
from sqlalchemy import desc

from sqlmodel import Session
from database import get_session
from models.models import PlatosCategoria
from interfaces.interfaces import GenericInterface, UsuarioResponse
from .dto.plato_categoria_dto import PlatoCategoriaDto
from utilidades.seguridad import get_current_user


router = APIRouter(prefix="/platos-categoria", tags=["Platos Categorías"])


@router.get("/", response_model=list[PlatosCategoria])
async def index(session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    return session.query(PlatosCategoria).order_by(desc(PlatosCategoria.id)).all()


@router.get("/{id}", response_model=PlatosCategoria)
async def show(id:int, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(PlatosCategoria, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no encontró el registro)"
        )
    return dato


@router.post("/", response_model=GenericInterface)
async def create(dto: PlatoCategoriaDto, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    existe = session.query(PlatosCategoria).filter(PlatosCategoria.nombre==dto.nombre).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (Ya existe en la bd)"
        )
    dato_db = PlatosCategoria(nombre=dto.nombre, slug=slugify(dto.nombre))
    try:
        #session.rollback()
        session.add(dato_db)
        session.commit()
        session.refresh(dato_db)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"estado":"ok", "mensaje":"Se crea el registro exitosamente"}
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (Se rompio algó en la bd)"
        )


@router.put("/{id}", response_model=PlatosCategoria)
async def update(id:int, dto: PlatoCategoriaDto, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(PlatosCategoria, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no encontró el registro)"
        )
    try:
        dato.nombre = dto.nombre
        dato.slug = slugify(dto.nombre)

        session.commit()
        session.refresh(dato)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"estado":"ok", "mensaje":"Se modifica el registro exitosamente"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ocurrió un error inesperado (Se rompio algó en la bd) error={e}"
        )


@router.delete("/{id}", response_model=PlatosCategoria)
async def destroy(id:int, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(PlatosCategoria, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no encontró el registro)"
        )
    try:
        session.delete(dato)
        session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"estado":"ok", "mensaje":"Se elimina el registro exitosamente"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ocurrió un error inesperado (Se rompio algó en la bd) error={e}"
        )