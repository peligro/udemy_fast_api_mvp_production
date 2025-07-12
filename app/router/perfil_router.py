from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session
from sqlalchemy import desc

from utilidades.seguridad import get_current_user
from database import get_session
from interfaces.interfaces import GenericInterface, UsuarioResponse
from models.models import Perfil
from .dto.perfil_dto import PerfilDto


router = APIRouter(prefix="/perfil", tags=["Perfil"])

@router.get("/", response_model=list[Perfil])
async def index(session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    datos = session.query(Perfil).order_by(desc(Perfil.id)).all()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[estado.model_dump() for estado in datos],
    )  

@router.get("/{id}", response_model=Perfil)
async def show(id: int, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Perfil, id)
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
async def create(dto: PerfilDto, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    # Personaliza el nombre antes de guardarlo
    dto.nombre = f"{dto.nombre}"
    # 👇 Validación antes de entrar al try
    existe = session.query(Perfil).filter(Perfil.nombre == dto.nombre).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (Ya existe un registro con ese nombre)"
        )
    try:
        dato_db = Perfil(**dto.model_dump())
        
        session.add(dato_db)
        session.commit()
        session.refresh(dato_db)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"estado": "ok", "mensaje": "Se crea el registro exitosamente"},
        )

    except Exception as e:
        session.rollback()  # Revierte cualquier cambio pendiente
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Ocurrió un error al crear el registro", "detalle": str(e)}
        )


@router.put("/{id}", response_model=GenericInterface)
async def update(id: int, dto: PerfilDto, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Perfil, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Recurso no disponible"}
        )
    try:
        dato.nombre = dto.nombre

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
    dato = session.get(Perfil, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible (No existe el registro)"
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
