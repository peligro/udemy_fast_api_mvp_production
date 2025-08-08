from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from .dto.ejemplo_dto import EjemploDto


router = APIRouter(prefix="/ejemplo", tags=["Ejemplo"])


@router.get("/")
async def index():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"estado":"ok", "mensaje":"Método GET"}
    )


@router.get("/{id}")
async def show(id: int):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"estado":"ok", "mensaje":f"Método GET | id={id}"}
    )


@router.post("/")
async def create(dto: EjemploDto):
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"estado":"ok", "mensaje":f"Método POST | nombre={dto.nombre} | descripcion={dto.descripcion} | precio={dto.precio} | verdadero={dto.verdadero}"}
    )

"""
@router.post("/")
async def create():
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"estado":"ok", "mensaje":"Método POST"}
    )
"""
@router.put("/{id}")
async def update(id: int):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"estado":"ok", "mensaje":f"Método PUT| id={id}"}
    )


@router.delete("/{id}")
async def destroy(id: int):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"estado":"ok", "mensaje":f"Método DELETE| id={id}"}
    )
    