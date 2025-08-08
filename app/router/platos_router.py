from fastapi import APIRouter, status, Depends, HTTPException, Form, UploadFile, Query
from fastapi.responses import JSONResponse
from typing import Annotated
import uuid

import boto3
from database import get_session
from sqlmodel import Session, select
from models.models import Platos, Negocio, PlatosCategoria
from sqlalchemy import desc

from interfaces.interfaces import GenericInterface, PlatoResponse, UsuarioResponse
from utilidades.seguridad import get_current_user

#dotenv
from dotenv import load_dotenv
load_dotenv()
import os


router = APIRouter(prefix="/platos", tags=["Platos"])

#cliente S3 apuntando a localstack
if os.getenv('ENVIRONMENT')=="local":
    s3_client = boto3.client(
        "s3",
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('AWS_SECRET_ACCESS_URL')
    )
else:
    s3_client = boto3.client(
        "s3",
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )


@router.post("/", response_model=GenericInterface)
async def create(
                negocio_id: Annotated[int, Form()],
                platoscategoria_id: Annotated[int, Form()],
                nombre: Annotated[str, Form()],
                ingredientes: Annotated[str, Form()],
                precio: Annotated[int, Form()], 
                file: UploadFile,
                session: Session=Depends(get_session),
                _: UsuarioResponse = Depends(get_current_user)
                ):
    #validamos que existe el negocio
    negocio = session.get(Negocio, negocio_id)
    if not negocio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ocurrió un error inesperado (no existe el negocio)"
        )
    #validamos que existe el platocategoria_id
    platocategoria = session.get(PlatosCategoria, platoscategoria_id)
    if not platocategoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ocurrió un error inesperado (no existe el platocategoria)"
        )
    #validación: nombre duplicado en el mismo negocio
    existe = session.exec(
        select(Platos).where(Platos.nombre==nombre, Platos.negocio_id==negocio_id)
    ).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ocurrió un error inesperado (ya existe un plato con ese nombre para este negocio)"
        )
    #subimos el archivo a s3
    extension="0"
    if file.content_type=="image/jpeg":
        extension="jpg"
    if file.content_type=="image/png":
        extension="png"
    if extension=="0":
        return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"estado":"error", "mensaje":f"Ocurrió un error inesperado (no cumple con el formato)"}
    )
    archivo = f"{uuid.uuid4()}.{extension}"
    try:
        s3_client.upload_fileobj(
                file.file,
                os.getenv('S3_BUCKET_NAME'),
                f"archivos/{archivo}",
                ExtraArgs={"ContentType": file.content_type}
            )
    except Exception as e:
            return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"estado":"error", "mensaje":f"Ocurrió un error inesperado (Error al subir el archivo a S3) | detalle={str(e)}"}
        )
    #crear el registro en la BD
    dato_db=Platos(
         platoscategoria_id=platoscategoria_id,
         negocio_id=negocio_id,
         nombre=nombre,
         precio=precio,
         ingredientes=ingredientes,
         foto=archivo
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
            detail=f"Ocurrió un error inesperado ({str(e)})"
        )
    


@router.get("/", response_model=list[PlatoResponse])
async def listar(negocio_id: int = Query(...),session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user) ):
    #validar que existe el negocio
    #validamos que existe el negocio
    negocio = session.get(Negocio, negocio_id)
    if not negocio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ocurrió un error inesperado (no existe el negocio)"
        )
    datos = session.exec(
        select(Platos).order_by(desc(Platos.id)).where(Platos.negocio_id==negocio_id)
    ).all()

    resultado=[
          PlatoResponse(
              id=dato.id,
              nombre=dato.nombre,
              ingredientes=dato.ingredientes,
              precio=dato.precio,
              foto=(
                f"{os.getenv('AWS_BUCKET_URL')}{os.getenv('S3_BUCKET_NAME')}/archivos/{dato.foto}"
                if os.getenv('ENVIRONMENT')=='local'
                else f"https://{os.getenv('S3_BUCKET_NAME')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/archivos/{dato.foto}"
            ),
              platoscategoria=dato.platoscategoria.nombre if dato.platoscategoria else None
          )   for dato in datos
    ]
    return resultado


@router.delete("/{id}", response_model=GenericInterface)
async def destroy(id: int, session: Session=Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Platos, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ocurrió un error inesperado (no existe el plato)"
        )
    #preguntar si existe imagen de S3
    try:
        s3_client.head_object(Bucket=os.getenv('S3_BUCKET_NAME'), Key=f"archivos/{dato.foto}")
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code']=='404':
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ocurrió un error inesperado (El archivo no existe en S3)"
            )
        else:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ocurrió un error inesperado (Error al verificar el archivo)"
            )
    #borramos el archivo
    try:
        s3_client.delete_object(Bucket=os.getenv('S3_BUCKET_NAME'), Key=f"archivos/{dato.foto}")
    except Exception as e:
        return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ocurrió un error inesperado (Error al borrar el archivo)"
            )
    #borramos el registro de la BD
    try:
        session.delete(dato)
        session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"estado":"ok", "mensaje":"Se elimina el registro exitosamente"}
        )
    except Exception as e:
        return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ocurrió un error inesperado (Error se rompió algo en la bd)"
            )