from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse

from database import get_session
from sqlmodel import Session
from models.models import Estado
from sqlalchemy import desc

from interfaces.interfaces import GenericInterface, UsuarioResponse
from .dto.estado_dto import EstadoDto
from utilidades.seguridad import get_current_user


router = APIRouter(prefix="/estado", tags=["Estado"])


@router.get("/", response_model=list[Estado])
async def index(session: Session=Depends(get_session), current_user: UsuarioResponse = Depends(get_current_user)):
    print(current_user)
    #datos = session.query(Estado).all()
    datos = session.query(Estado).order_by(desc(Estado.id)).all()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[dato.model_dump() for dato in datos]
    )


@router.get("/{id}", response_model=Estado)
async def show(id:int, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Estado, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=dato.model_dump()
    )


@router.post("/", response_model=GenericInterface)
async def create(dto: EstadoDto, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #personalizar el nombre antes de guardarlo
    dto.nombre = f"{dto.nombre}"
    #validación antes de entra al try para que no se repita el nombre
    #select * from estado where nombre='dto.nombre'
    existe = session.query(Estado).filter(Estado.nombre==dto.nombre).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (Ya existe un estado con este nombre)"
        )
    #se crea el registro
    try:
        data_db = Estado(**dto.model_dump())
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
async def update(id: int, dto:EstadoDto, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Estado, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible"
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
        session.rollback() #Revierte cualquier cambio pendiente
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (algo se rompió, ya sea la bd)"
        )


@router.delete("/{id}", response_model=GenericInterface)
async def destroy(id: int, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Estado, id)
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