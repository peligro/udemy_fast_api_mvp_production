from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

#dotenv
from dotenv import load_dotenv
load_dotenv()
import os



# Importa la tarea de SQS
from worker.sqs_worker import iniciar_sqs_background_task


# Importamos la configuración de OpenAPI
from fastapi.openapi.docs import get_swagger_ui_html
from swagger.openapi import custom_openapi

#rutas
from router.ejemplo_router import router as ejemplo_router
from router.upload_router import router as upload_router
from router.estado_router import router as estado_router
from router.categoria_router import router as categoria_router
from router.negocio_router import router as negocio_router
from router.negocio_logo_router import router as negocio_logo_router
from router.platos_categoria_router import router as platos_categoria_router
from router.platos_router import router as platos_router
from router.carta_router import router as carta_router
from router.usuario_router import router as usuario_router
from router.login_router import router as login_router
from router.perfil_router import router as perfil_router
from router.recovery_router import router as recovery_router
from router.negocio_por_usuario_router import router as negocio_por_usuario_router

app = FastAPI(docs_url=None)

# Inicia la tarea background
iniciar_sqs_background_task(app)


# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los encabezados
)

#swagger
# Aplicamos la configuración de OpenAPI
app.openapi = custom_openapi(app)
# Middleware para servir la documentación de Swagger
@app.get("/documentacion", include_in_schema=False)
async def swagger_documentation():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="FastAPI - Documentación")

#@app.get("/", status_code=status.HTTP_200_OK)
@app.get("/")
def index():
    #print(os.getenv('AWS_REGION'))
    #return {"estado": "ok", "mensaje": "Fullstack FastAPI + SQLAlchemy + React + AWS"}
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"estado": "ok", "mensaje": "Fullstack FastAPI + SQLAlchemy + React + AWS"},
    )


# Incluir el router
app.include_router(ejemplo_router)
app.include_router(upload_router)
app.include_router(estado_router)
app.include_router(categoria_router)
app.include_router(negocio_router)
app.include_router(negocio_logo_router)
app.include_router(platos_categoria_router)
app.include_router(platos_router)
app.include_router(carta_router)
app.include_router(usuario_router)
app.include_router(login_router)
app.include_router(perfil_router)
app.include_router(recovery_router)
app.include_router(negocio_por_usuario_router)



#custom 404
@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def custom_404_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=404,
        content={"estado": "error", "mensaje": "Ruta no encontrada"},
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