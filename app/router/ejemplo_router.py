from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from .dto.ejemplo_dto import EjemploDto

router = APIRouter(prefix="/ejemplo", tags=["Ejemplo"])


@router.get("/")
async def index():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"estado": "ok", "mensaje": "Método GET"},
    )  



@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_item(id: int):
    return JSONResponse(
        status_code=200,
        content={"estado": "ok", "mensaje": f"Método GET con parámetro {id}"},
    ) 


"""
{
    "descripcion":"texto de la descripción",
    "nombre":"u",
    "precio":123456,
    "verdadero":true
}
"""
@router.post("/")
async def create(dto:EjemploDto):
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content= {"estado": "ok", "mensaje": f"Método POST | nombre:{dto.nombre} | descripción:{dto.descripcion} | precio:{dto.precio} | verdadero:{dto.verdadero}"},
    ) 
    

"""
@router.post("/", status_code=201)
async def create():
    return {"estado": "ok", "mensaje": "Método POST"}
"""

@router.put("/{id}")
async def update(id: int):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content= {"estado": "ok", "mensaje": f"Método PUT con parámetro {id}"},
    )  


@router.delete("/{id}")
async def destroy(id: int):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content= {"estado": "ok", "mensaje": f"Método DELETE con parámetro {id}"},
    )  