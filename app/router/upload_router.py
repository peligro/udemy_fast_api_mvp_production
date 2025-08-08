from fastapi import APIRouter, status, Form, UploadFile, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Annotated
import uuid
import os
import boto3

#dotenv
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/upload", tags=["Subir archivos"])


#cliente S3 apuntando a localstack
s3_client = boto3.client(
    "s3",
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    endpoint_url=os.getenv('AWS_SECRET_ACCESS_URL')
)
S3_BUCKET_NAME=os.getenv('S3_BUCKET_NAME')


#subiendo archivo al servidor
@router.post("/")
async def subir( negocio_id: Annotated[int, Form()], file: UploadFile ):
    #print(file)
    extesion="0"
    if file.content_type=="image/jpeg":
        extesion="jpg"
    if file.content_type=="image/png":
        extesion="png"
    if extesion=="0":
        return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"estado":"error", "mensaje":f"Ocurrió un error inesperado (no cumple con el formato)"}
    )
    else:
        #generar un nombre único
        nombre = f"{uuid.uuid4()}.{extesion}"
        try:
            s3_client.upload_fileobj(
                file.file,
                S3_BUCKET_NAME,
                f"archivos/{nombre}",
                ExtraArgs={"ContentType": file.content_type}
            )
        except Exception as e:
            return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"estado":"error", "mensaje":f"Ocurrió un error inesperado (Error al subir el archivo a S3) | detalle={str(e)}"}
        )
        file_url=f"http://localhost:8000/{S3_BUCKET_NAME}/archivos/{nombre}"
        #retornamos una respuesta
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"estado":"ok", "mensaje":f"Método post | negocio_id={negocio_id}", "filename":file.filename, "size":file.size, "mimetype":file.content_type, "nombre":nombre, "url":file_url}
        )


#eliminar recurso del bucket S3
@router.delete("/file")
async def ejemplo_foto(file_name: str = Query(..., descripction="Nombre del archivo a borrar")):
    #preguntamos si existe el recurso en el bucket
    try:
        s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=f"archivos/{file_name}")
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code']=='404':
            return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"estado":"error", "mensaje":f"Ocurrió un error inesperado (El archivo no existe en el bucket)"}
            )
        else:
            return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"estado":"error", "mensaje":f"Ocurrió un error inesperado (Error al verificar el archivo)"}
            )
    #borrar el archivo
    try:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=f"archivos/{file_name}")
    except:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"estado":"error", "mensaje":f"Ocurrió un error inesperado (Error al borrar el archivo)"}
            )
    
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"estado":"ok", "mensaje":f"Se borra el archivo exitosamente"}
            )


"""
#subiendo archivo al servidor
@router.post("/")
async def subir( negocio_id: Annotated[int, Form()], file: UploadFile ):
    #print(file)
    extesion="0"
    if file.content_type=="image/jpeg":
        extesion="jpg"
    if file.content_type=="image/png":
        extesion="png"
    if extesion=="0":
        return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"estado":"error", "mensaje":f"Ocurrió un error inesperado (no cumple con el formato)"}
    )
    else:
        #generar un nombre único
        nombre = f"{uuid.uuid4()}.{extesion}"
        file_location= os.path.join("uploads", nombre)
        #guardar el archivo en disco
        with open(file_location, "wb") as buffer:
            buffer.write(await file.read())
        #retornamos una respuesta
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"estado":"ok", "mensaje":f"Método post | negocio_id={negocio_id}", "filename":file.filename, "size":file.size, "mimetype":file.content_type, "nombre":nombre}
        )
"""


#renderización dinámica archivo con FileResponse y querystring
@router.get("/file")
async def ejemplo_foto(id: str = Query(..., descripction="Nombre del archivo")):
    if not os.path.exists(f"uploads/{id}"):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"estado":"error", "mensaje":f"Ocurrió un error inesperado (archivo no existe)"}
        )
    return FileResponse(f"uploads/{id}")


"""
#validar el tipo de archivo con mimetype
@router.post("/")
async def subir( negocio_id: Annotated[int, Form()], file: UploadFile ):
    #print(file)
    extesion="0"
    if file.content_type=="image/jpeg":
        extesion="jpg"
    if file.content_type=="image/png":
        extesion="png"
    if extesion=="0":
        return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"estado":"error", "mensaje":f"Ocurrió un error inesperado (no cumple con el formato)"}
    )
    else:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"estado":"ok", "mensaje":f"Método post | negocio_id={negocio_id}", "filename":file.filename, "size":file.size, "mimetype":file.content_type}
        )
"""


"""
#recibir valor formdata y de tipo file
@router.post("/")
async def subir( negocio_id: Annotated[int, Form()], file: UploadFile ):
    #print(file)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"estado":"ok", "mensaje":f"Método post | negocio_id={negocio_id}", "filename":file.filename, "size":file.size, "mimetype":file.content_type}
    )
"""


"""
#recibir valores formdata
@router.post("/")
async def subir( negocio_id: Annotated[int, Form()] ):
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"estado":"ok", "mensaje":f"Método post | negocio_id={negocio_id}"}
    )
"""


