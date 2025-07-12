from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session
from sqlalchemy import desc
from utilidades.seguridad import get_current_user


from database import get_session
from interfaces.interfaces import GenericInterface, UsuarioResponse
from models.models import Estado
from .dto.estado_dto import EstadoDto


router = APIRouter(prefix="/estado", tags=["Estado"])

@router.get("/", response_model=list[Estado])
async def index(session: Session = Depends(get_session), current_user: UsuarioResponse = Depends(get_current_user)):
    #datos = session.query(Estado).all()
    #print(current_user)
    datos = session.query(Estado).order_by(desc(Estado.id)).all()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[estado.model_dump() for estado in datos],
    )  

@router.get("/{id}", response_model=Estado)
async def show(id: int, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Estado, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Recurso no disponible"}
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=dato.model_dump()
    )



@router.post("/", response_model=GenericInterface)
async def create(dto: EstadoDto, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    # Personaliza el nombre antes de guardarlo
    dto.nombre = f"{dto.nombre}"
    # 👇 Validación antes de entrar al try
    existe = session.query(Estado).filter(Estado.nombre == dto.nombre).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Ya existe un estado con ese nombre"}
        )
    try:
        estado_db = Estado(**dto.model_dump())
        
        session.add(estado_db)
        session.commit()
        session.refresh(estado_db)

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

"""
@router.post("/", response_model=GenericInterface)
async def create(dto: EstadoDto, session: Session = Depends(get_session)):
    # Personaliza el nombre antes de guardarlo
    dto.nombre = f"{dto.nombre}"
    try:
        estado_db = Estado(**dto.model_dump())
        
        session.add(estado_db)
        session.commit()
        session.refresh(estado_db)

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
"""

"""
@router.post("/", response_model=GenericInterface)
async def create(dto: EstadoDto, session: Session = Depends(get_session)):
    # Personaliza el nombre antes de guardarlo
    dto.nombre = f"{dto.nombre}_lindo"
    estado_db = Estado(**dto.model_dump())
    
    session.add(estado_db)
    session.commit()
    session.refresh(estado_db)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"estado": "ok", "mensaje": f"Se crea el registro exitosamente"},
    )  

"""

@router.put("/{id}", response_model=GenericInterface)
async def update(id: int, dto: EstadoDto, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Estado, id)
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
async def destroy(id: int, session: Session = Depends(get_session)):
    dato = session.get(Estado, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Recurso no disponible"}
        )
    try:
        session.delete(dato)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Ocurrió un error inesperado" }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content= {"estado": "ok", "mensaje": f"Se elimina el registro exitosamente"},
    )  
