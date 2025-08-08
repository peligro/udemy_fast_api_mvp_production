from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import desc

from database import get_session
from sqlmodel import Session
from models.models import Perfil
from interfaces.interfaces import GenericInterface, UsuarioResponse
from .dto.perfil_dto import PerfilDto
from utilidades.seguridad import get_current_user


router = APIRouter(prefix="/perfil", tags=["Perfil"])

@router.get("/", response_model=list[Perfil])
async def index(session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    datos = session.query(Perfil).order_by(desc(Perfil.id)).all()
    #return datos
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[dato.model_dump() for dato in datos ]
    )


@router.get("/{id}", response_model=Perfil)
async def show(id:int, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Perfil, id)
    if  not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el perfil)"
        )
    #return datos
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=dato.model_dump()
    )


@router.post("/", response_model=GenericInterface)
async def create(dto:PerfilDto, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #dto.nombre= f"{dto.nombre}"
    existe = session.query(Perfil).filter(Perfil.nombre==dto.nombre).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (Ya exsite un registro con ese nombre)"
        )
    try:
        dato_db = Perfil(**dto.model_dump())
        session.add(dato_db)
        session.commit()
        session.refresh(dato_db)
        return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"estado":"ok", "mensaje":"Se crea el registro exitosamente"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ocurrió un error inesperado (falló, se rompió la BD) | {str(e)}"
        )


@router.put("/{id}", response_model=GenericInterface)
async def update(id:int, dto: PerfilDto, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Perfil, id)
    if  not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el perfil)"
        )
    try:
        dato.nombre= dto.nombre
        session.commit()
        session.refresh(dato)
        return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"estado":"ok", "mensaje":"Se modifica el registro exitosamente"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ocurrió un error inesperado (falló, se rompió la BD) | {str(e)}"
        )
    

@router.delete("/{id}", response_model=GenericInterface)
async def destroy(id:int, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Perfil, id)
    if  not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el perfil)"
        )
    try:
        session.delete(dato)
        session.commit()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ocurrió un error inesperado (falló, se rompió la BD) | {str(e)}"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"estado":"ok", "mensaje":"Se elimina el registro exitosamente"}
        )