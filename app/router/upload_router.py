from fastapi import APIRouter, Query, Form, File, UploadFile, status
from fastapi.responses import JSONResponse
from typing import Annotated
import boto3
import uuid
from dotenv import load_dotenv
load_dotenv()
import os

router = APIRouter(prefix="/upload", tags=["Subir archivos"])

# Cliente S3 apuntando a LocalStack
s3_client = boto3.client(
    "s3",
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    endpoint_url=os.getenv('AWS_SECRET_ACCESS_URL')
)

S3_BUCKET_NAME = "curso-udemy"

@router.post("/")
async def create(producto_id: Annotated[int, Form()], file: UploadFile):
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
            S3_BUCKET_NAME,
            f"archivos/{nombre}",
            ExtraArgs={"ContentType": file.content_type}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "INTERNAL SERVER ERROR", "mensaje": "Error al subir archivo a S3", "detalle": str(e)},
        )

    file_url = f"http://localhost:8000/{S3_BUCKET_NAME}/archivos/{nombre}"

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "producto_id": producto_id,
            "original_name": file.filename,
            "saved_name": nombre,
            "mimetype": file.content_type,
            "url": file_url
        },
    )


@router.delete("/file")
async def delete_file(file_name: str = Query(..., description="Nombre del archivo a borrar")):
    try:
        s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=f"archivos/{file_name}")
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": "NOT FOUND", "mensaje": "El archivo no existe en S3"}
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "BAD REQUEST", "mensaje": "Error al verificar el archivo", "detalle": str(e)}
            )

    try:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=f"archivos/{file_name}")
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "BAD REQUEST", "mensaje": "Error al borrar archivo de S3", "detalle": str(e)},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"estado": "ok", "mensaje": f"Archivo {file_name} borrado correctamente"}
    )

"""
#subiendo archivos al servidor
@router.post("/")
async def create(producto_id: Annotated[int, Form()], file: UploadFile):
    extension="0"
    if file.content_type=="image/jpeg":
        extension="jpg"
    if file.content_type=="image/png":
        extension="png"
    if extension=="0": 
        return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content= {"error": "BAD REQUEST", "mensaje": "Ocurrió un error inesperado"},
    )
    else:
         # Generar un nombre único
        nombre = f"{uuid.uuid4()}.{extension}"
        file_location = os.path.join("uploads", nombre)
        # Guardar archivo en disco
        with open(file_location, "wb") as buffer:
            buffer.write(await file.read())
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content= {"producto_id": producto_id, "filename": file.filename, "size": file.size, "mimetype": file.content_type, "nombre": nombre},
        ) 

#Renderización archivo con FileResponse y querystring
#http://127.0.0.1:8090/upload/file?id=d9ccd8e3-cd1d-4972-9599-e29177d710ad.jpg
@router.get("/file", status_code=status.HTTP_200_OK)
async def ejemplo_foto(id: str = Query(..., description="Nombre del archivo")):
    if not os.path.exists(f"uploads/{id}"):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content= {"estado": "error", "mensaje":"Recurso no disponible"},
        ) 
    return FileResponse(f"uploads/{id}")
"""

"""
#validar mimetype de archivo a subir
@router.post("/")
async def create(producto_id: Annotated[int, Form()], file: UploadFile):
    extension="0"
    if file.content_type=="image/jpeg":
        extension="jpg"
    if file.content_type=="image/png":
        extension="png"
    if extension=="0": 
        return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content= {"error": "BAD REQUEST", "mensaje": "Ocurrió un error inesperado"},
    )
    else:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content= {"producto_id": producto_id, "filename": file.filename, "size": file.size, "mimetype": file.content_type},
        ) 

"""

"""
#Recibiendo archivo vía FormData con UploadFile
@router.post("/")
async def create(producto_id: Annotated[int, Form()], file: UploadFile):
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content= {"producto_id": producto_id, "filename": file.filename, "size": file.size, "mimetype": file.content_type},
    )  
"""
"""
#recibiendo formdata
@router.post("/")
async def create(producto_id: Annotated[int, Form()]):
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content= {"estado": "ok", "mensaje": f"Método POST upload | username={producto_id}"},
    ) 
"""


"""
@router.post("/")
def create():
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content= {"estado": "ok", "mensaje": f"Método POST upload"},
    ) 
"""