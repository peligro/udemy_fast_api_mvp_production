from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import desc

from database import get_session
from sqlmodel import Session, select
from models.models import Perfil, Usuario, Estado, Negocio
from interfaces.interfaces import GenericInterface, UsuarioResponse
from .dto.usuario_dto import UsuarioDto
from utilidades.utilidades import formatear_fecha, generate_hash
from utilidades.seguridad import get_current_user


router = APIRouter(prefix="/usuario", tags=["Usuario"])


@router.get("/", response_model=list[UsuarioResponse])
async def index(session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    datos = session.query(Usuario).order_by(desc(Usuario.id)).all()
    
    resultado = [
        UsuarioResponse(
            id = dato.id,
            nombre=dato.nombre,
            correo = dato.correo,
            telefono = dato.telefono,
            estado_id = dato.estado_id,
            estado = dato.estado.nombre,
            perfil_id= dato.perfil_id,
            perfil = dato.perfil.nombre,
            fecha = formatear_fecha(dato.fecha)
        ) for dato in datos
    ]
    return resultado


@router.get("/{id}", response_model=UsuarioResponse)
async def show(id: int, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Usuario, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el usuario)"
        )
    return {
        "id": dato.id,
        "nombre": dato.nombre,
        "correo": dato.correo,
        "telefono": dato.telefono,
        "estado_id": dato.estado_id,
        "estado": dato.estado.nombre,
        "perfil_id": dato.perfil_id,
        "perfil": dato.perfil.nombre,
        "fecha": formatear_fecha(dato.fecha)
    }


@router.post("/", response_model=GenericInterface)
async def create(dto: UsuarioDto, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validamos si existe el perfil
    perfil = session.get(Perfil, dto.perfil_id)
    if not perfil:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el perfil)"
        )
    #validamos correo duplicado
    existe = session.query(Usuario).filter(Usuario.correo==dto.correo).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (ya existe un registro con ese correo)"
        )
    dato_db = Usuario(
        estado_id=1,
        perfil_id=dto.perfil_id,
        nombre = dto.nombre,
        correo = dto.correo,
        telefono = dto.telefono,
        token = '',
        password= generate_hash(dto.password)
    )
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ocurrió un error inesperado (ya existe un registro con ese correo) | {str(e)}"
        )



@router.put("/{id}", response_model=GenericInterface)
async def update(id: int, dto: UsuarioDto, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validamos si existe el perfil
    perfil = session.get(Perfil, dto.perfil_id)
    if not perfil:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el perfil)"
        )
    estado = session.get(Estado, dto.estado_id)
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el estado_id)"
        )
    dato = session.get(Usuario, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el usuario)"
        )
    dato.nombre = dto.nombre
    dato.perfil_id = dto.perfil_id
    dato.estado_id = dto.estado_id,
    dato.correo = dto.correo
    dato.telefono = dto.telefono
    if dto.editar ==1:
        dato.password= generate_hash(dto.password)
    try:
        session.commit()
        session.refresh(dato)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ocurrió un error inesperado (ya existe un registro con ese correo) | {str(e)}"
        )
    

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"estado":"ok", "mensaje":"Se modifica el registro exitosamente"}
        )


@router.delete("/{id}", response_model=GenericInterface)
async def destroy(id: int, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Usuario, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el usuario)"
        )
    
    negocio = session.exec(
        select(Negocio).where(Negocio.usuario_id==id)
    ).first()
    if negocio:
       raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no se puede eliminar porque existe en negocio)"
        ) 
    try:
        session.delete(dato)
        session.commit()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ocurrió un error inesperado (error en la BD) | {str(e)}"
        )
    

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"estado":"ok", "mensaje":"Se elimina el registro exitosamente"}
        )