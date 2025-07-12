from fastapi import APIRouter, Depends, status, HTTPException, Form, UploadFile
from fastapi.responses import JSONResponse
from sqlmodel import Session


from typing import Annotated
import boto3
import uuid
from dotenv import load_dotenv
load_dotenv()
import os
from utilidades.seguridad import get_current_user
from database import get_session
from interfaces.interfaces import GenericInterface, UsuarioResponse
from models.models import Negocio


router = APIRouter(prefix="/negocio-logo", tags=["Negocios logo"])

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
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    )



@router.post("/", response_model=GenericInterface)
async def create(id: Annotated[int, Form()], file: UploadFile, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validamos que existe el negocio
    dato = session.get(Negocio, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible"
        )
    logo=dato.logo
    
    #subimos el archivo
    extension = None
    if file.content_type == "image/jpeg":
        extension = "jpg"
    elif file.content_type == "image/png":
        extension = "png"
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "BAD REQUEST", "mensaje": "Formato de imagen no permitido"},
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
            content={"error": "BAD REQUEST", "mensaje": "Error al subir archivo a S3", "detalle": str(e)},
        )
    #actualizamos el valor del logo en la BD
    try:
        dato.logo = f"{nombre}"
        session.commit()
        session.refresh(dato)
        
    except Exception as e:
        session.rollback()  # Revierte cualquier cambio pendiente
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Ocurrió un error inesperado" }
        )
    
    #borramos el archivo anterior de la BD
    #print(f"logo={logo} | dato.logo = {dato.logo}")
    if logo=="default.png":
        pass
    else:
        try:
            s3_client.delete_object(Bucket=os.getenv('S3_BUCKET_NAME'), Key=f"archivos/{logo}")
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content="Error al borrar archivo de S3",
            )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "estado": "ok",
            "mensaje": "Se modifica el registro exitosamente"
        },
    )






