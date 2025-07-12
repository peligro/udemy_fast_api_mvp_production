from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from utilidades.seguridad import get_current_user
from fastapi.responses import RedirectResponse

import time
import uuid
from dotenv import load_dotenv
load_dotenv()
import os

from database import get_session
from utilidades.utilidades import generate_hash
from interfaces.interfaces import GenericInterface, UsuarioResponse
from models.models import Usuario
from .dto.recovery_dto import RecoveryDto
from .dto.recovery_update_dto import RecoveryUpdateDto

#aws
import boto3
from botocore.exceptions import ClientError

router = APIRouter(prefix="/recovery", tags=["Recovery"])

if os.getenv('ENVIRONMENT')=="local":
    sqs_client = boto3.client(
    "sqs",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "fake"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "fake"),
    endpoint_url=os.getenv("AWS_SECRET_ACCESS_URL")
)
else:
    sqs_client = boto3.client(
    "sqs",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "fake"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "fake"),
)


@router.post("/update/{token}")
async def update(token: str, dto: RecoveryUpdateDto, session: Session = Depends(get_session)):
    dato = session.exec(
        select(Usuario).where(Usuario.token == token, Usuario.estado_id == 1)
    ).first()

    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (No existe el token)"
        )
    try:
        dato.password = generate_hash(dto.password)
        dato.token=''

        session.commit()
        session.refresh(dato)
        #redireccionar aquí
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"estado": "ok", "mensaje": "Se modifica el registro exitosamente"},
        )
    except Exception as e:
        session.rollback()  # Revierte cualquier cambio pendiente
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"estado": "error", "mensaje": "Ocurrió un error inesperado" }
        )


@router.post("/restablecer", response_model=GenericInterface)
async def create(dto: RecoveryDto, session: Session = Depends(get_session) ):
    # Buscar al usuario por correo
    dato = session.exec(
        select(Usuario).where(Usuario.correo == dto.correo, Usuario.estado_id == 1)
    ).first()

    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (No existe el correo)"
        )

    token = f"{uuid.uuid4()}{int(time.time())}{uuid.uuid4()}"
    url = f"{os.getenv('BASE_URL_FRONTEND')}/recovery/update/{token}"

    try:
        # Actualizamos el token del usuario
        dato.token = token
        session.commit()
        session.refresh(dato)

        # Enviamos mensaje a la cola SQS
        sqs_client.send_message(
            QueueUrl=os.getenv("SQS_ENVIO_CORREO"),
            MessageBody=url,
            MessageAttributes={
                'Nombre': {
                    'DataType': 'String',
                    'StringValue': dato.nombre
                },
                'Token': {
                    'DataType': 'String',
                    'StringValue': token
                }
            }
        )

        
        return GenericInterface(estado="ok", mensaje="Se modifica el registro exitosamente")

    except ClientError as ce:
        session.rollback()
        error_code = ce.response['Error']['Code']
        error_msg = ce.response['Error']['Message']
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"code error={error_code} | message={error_msg}"
        ) from ce

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (al editar el registro)"
        ) from e

