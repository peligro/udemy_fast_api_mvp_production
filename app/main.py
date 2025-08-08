from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from swagger.openapi import custom_openapi
from fastapi.openapi.docs import get_swagger_ui_html

#dotenv
from dotenv import load_dotenv
load_dotenv()
import os

#rutas
from router.ejemplo_router import router as ejemplo_router
from router.upload_router import router as upload_router
from router.estado_router import router as estado_router
from router.categoria_router import router as categoria_router
from router.negocio_router import router as negocio_router
from router.negocio_logo_router import router as negocio_logo_router
from router.negocio_por_usuario_router import router as negocio_por_usuario_router
from router.plato_categoria_router import router as plato_categoria_router
from router.platos_router import router as platos_router
from router.carta_router import router as carta_router
from router.perfil_router import router as perfil_router
from router.usuario_router import router as usuario_router
from router.recovery_router import router as recovery_router
from router.login_router import router as login_router


#importar la tarea de SQS
from worker.sqs_worker import iniciar_sqs_background_task


#inicializamos FastAPI
app = FastAPI()

#iniciar la tarea background
iniciar_sqs_background_task(app)

#configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#swagger
app.openapi = custom_openapi(app)
@app.get("/documentacion", include_in_schema=False)
async def swagger_documentation():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="FastAPI - Documentación")


#generar una ruta
@app.get("/")
def index():
    #return {"estado":"ok", "mensaje":"Fullstack FastAPI + SQLaLCHEMY + React + AWS"}
    #print("hola qué tal")
    #print(f"el valor de la variable AWS_REGION={os.getenv('AWS_REGION')}")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"estado":"oks", "mensaje":"Fullstack FastAPI + SQLaLCHEMY + React + AWS"}
    )

"""
def index():
    return "hola"
"""


#incluimos las rutas del router
app.include_router(ejemplo_router)
app.include_router(upload_router)
app.include_router(estado_router)
app.include_router(categoria_router)
app.include_router(negocio_router)
app.include_router(negocio_logo_router)
app.include_router(negocio_por_usuario_router)
app.include_router(plato_categoria_router)
app.include_router(platos_router)
app.include_router(carta_router)
app.include_router(perfil_router)
app.include_router(usuario_router)
app.include_router(recovery_router)
app.include_router(login_router)


#custom 404
@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def custom_404_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"estado":"error", "mensaje":"Ruta no encontrada"}
    )


#para métodos HTTP no usados {"detail": "Method Not Allowed"}
@app.exception_handler(StarletteHTTPException)
async def custom_405_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        return JSONResponse(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            content={"estado": "error", "mensaje": "Método no permitido"},
        )
    # Para otras excepciones que puedan llegar aquí
    return JSONResponse(
        status_code=exc.status_code,
        content={"estado": "error", "mensaje": str(exc.detail)},
    )


#validaciones dto
@app.exception_handler(RequestValidationError)
async def manejar_errores_validacion(request: Request, exc: RequestValidationError):
    errores_personalizados = []

    for error in exc.errors():
        campo = error["loc"][-1]
        mensaje = error["msg"]

        # Procesar ValueError con ("campo", "mensaje")
        if mensaje.startswith("Value error,"):
            try:
                _, custom_msg = eval(error["input"])
                mensaje = custom_msg
            except:
                pass

        elif mensaje == "Input should be a valid integer":
            mensaje = f"El campo {campo} debe ser un número entero"

        elif mensaje == "Field required":
            mensaje = f"El campo {campo} es obligatorio"

        errores_personalizados.append({
            "campo": campo,
            "mensaje": mensaje
        })

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "estado": "error",
            "mensaje": "Errores de validación",
            "errores": errores_personalizados
        },
    )


# docker exec -it python_service uvicorn main:app --host 0.0.0.0 --port 8050 --reload


