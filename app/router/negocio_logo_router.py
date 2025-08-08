from fastapi import APIRouter, status, Depends, HTTPException, Form, UploadFile
from fastapi.responses import JSONResponse

from typing import Annotated
import uuid

from models.models import Negocio
from database import get_session
from sqlmodel import Session


import boto3
from interfaces.interfaces import GenericInterface, UsuarioResponse
from utilidades.seguridad import get_current_user

#dotenv
from dotenv import load_dotenv
load_dotenv()
import os


router = APIRouter(prefix="/negocio-logo", tags=["Negocios logo"])

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
async def subir( id: Annotated[int, Form()], file: UploadFile, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validar que existe el negocio
    dato = session.get(Negocio, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no disponible"
        )
    #dejamos esta variable logo, para eventualmente borrarlo mas adelante si es necesario
    logo = dato.logo
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
    nombre = f"{uuid.uuid4()}.{extension}"
    try:
        s3_client.upload_fileobj(
                file.file,
                os.getenv('S3_BUCKET_NAME'),
                f"archivos/{nombre}",
                ExtraArgs={"ContentType": file.content_type}
            )
    except Exception as e:
            return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"estado":"error", "mensaje":f"Ocurrió un error inesperado (Error al subir el archivo a S3) | detalle={str(e)}"}
        )
    #actualizar el valor del logo en la BD
    try:
        dato.logo = nombre
        session.commit()
        session.refresh(dato)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detailt="Ocurrió un error inesperado (erro se rompe la bd)"
        )
    #borramos el archivo anterior del S3
    if logo == os.getenv('S3_LOGO_NEGOCIO'):
        pass
    else:
        try:
            s3_client.delete_object(Bucket=os.getenv('S3_BUCKET_NAME'), Key=f"archivos/{logo}")
        except Exception as e:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detailt="Ocurrió un error inesperado (error al borrar el archivo del S3)"
        )
    return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"estado":"ok", "mensaje":f"Se modifica el registro exitosamente"}
        )
    