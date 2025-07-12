from fastapi import APIRouter, Depends, status, HTTPException, Query, UploadFile, Form
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from sqlalchemy import desc

#aws
from typing import Annotated
import boto3
import uuid
from dotenv import load_dotenv
load_dotenv()
import os


from utilidades.seguridad import get_current_user
from database import get_session
from interfaces.interfaces import GenericInterface, PlatoResponse, UsuarioResponse
from models.models import Platos, Negocio, PlatosCategoria


router = APIRouter(prefix="/platos", tags=["Platos"])

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
async def create(
                negocio_id: Annotated[int, Form()], 
                platoscategoria_id: Annotated[int, Form()], 
                nombre: Annotated[str, Form()],
                ingredientes: Annotated[str, Form()],
                precio: Annotated[int, Form()], 
                file: UploadFile, 
                session: Session = Depends(get_session),
                _: UsuarioResponse = Depends(get_current_user)):
    #validamos que existe el negocio
    dato = session.get(Negocio, negocio_id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible (no existe negocio)"
        )
    #validamos que existe el platoscategoria_id
    dato2 = session.get(PlatosCategoria, platoscategoria_id)
    if not dato2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible (no existe platoscategoria)"
        )
    # Validación: nombre duplicado en el mismo negocio
    existe = session.exec(
        select(Platos).where(Platos.nombre == nombre, Platos.negocio_id == negocio_id)
    ).first()

    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un plato con ese nombre para este negocio"
        )
    
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
            content={"error": "BAD REQUEST", "mensaje": "Error al subir archivo a S3", "detalle": str(e)},
        )
    #actualizamos el valor del logo en la BD
    dato_db = Platos(
        platoscategoria_id=platoscategoria_id,
        negocio_id=negocio_id,
        nombre=nombre, 
        precio=precio,
        ingredientes=ingredientes,
        foto=archivo
        )
    
    try:
        session.rollback()
        session.add(dato_db)
        session.commit()
        session.refresh(dato_db)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"estado": "ok", "mensaje": "Se crea el registro exitosamente"},
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Ocurrió un error al crear el registro", "detalle": str(e)}
        )



#http://localhost:8050/platos?negocio_id=7
@router.get("/", response_model=list[PlatoResponse])
async def listar(negocio_id: int = Query(...), session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    #validamos que existe el negocio
    dato = session.get(Negocio, negocio_id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible (no existe el negocio)"
        )
    platos = session.exec(
        select(Platos).order_by(desc(Platos.id)).where(Platos.negocio_id == negocio_id)
    ).all()

   

    resultado = [
        PlatoResponse(
            id=plato.id,
            nombre=plato.nombre,
            ingredientes=plato.ingredientes,
            precio=plato.precio,
            foto=f"{os.getenv('AWS_BUCKET_URL')}{os.getenv('S3_BUCKET_NAME')}/archivos/{plato.foto}",
            platoscategoria=plato.platoscategoria.nombre if plato.platoscategoria else None
        ) for plato in platos
    ]

    return resultado



@router.delete("/{id}", response_model=GenericInterface)
async def destroy(id: int, session: Session = Depends(get_session), _: UsuarioResponse = Depends(get_current_user)):
    dato = session.get(Platos, id)
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurso no disponible (no existe el plato)"
        )
    #borramos imagen de S3
    try:
        s3_client.head_object(Bucket=os.getenv('S3_BUCKET_NAME'), Key=f"archivos/{dato.foto}")
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content="El archivo no existe en S3"
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content="Error al verificar el archivo"
            )

    try:
        s3_client.delete_object(Bucket=os.getenv('S3_BUCKET_NAME'), Key=f"archivos/{dato.foto}")
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Error al borrar archivo de S3",
        )
    #borramos registro
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