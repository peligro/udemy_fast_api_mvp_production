from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse


from database import get_session
from sqlmodel import Session, select
from interfaces.interfaces import GenericInterface
from models.models import  Usuario
from .dto.recovery_dto import RecoveryDto, RecoveryUpdateDto
from utilidades.utilidades import generate_hash

import time
import uuid
import os
from dotenv import load_dotenv
load_dotenv()
import boto3
from botocore.exceptions import ClientError


router = APIRouter(prefix="/recovery", tags=["Recovery"])

if os.getenv('ENVIRONMENT')=="local":
    sqs_client= boto3.client(
        "sqs",
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('AWS_SECRET_ACCESS_URL')
    )
else:
    sqs_client= boto3.client(
        "sqs",
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )



@router.post("/update/{token}")
async def update(token: str, dto: RecoveryUpdateDto, session: Session=Depends(get_session)):
    dato = session.exec(
        select(Usuario).where(Usuario.token == token, Usuario.estado_id == 1)
    ).first()
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el token)"
        )
    try:
        dato.password= generate_hash(dto.password)
        dato.token=''
        session.commit()
        session.refresh(dato)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"estado":"ok", "mensaje":"Se modifica el registro exitosamente"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no se pudo actualizar)"
        )


@router.post("/restablecer", response_model=GenericInterface)
async def create(dto: RecoveryDto, session: Session=Depends(get_session)):
    #buscar al usuario activo por correo
    dato = session.exec(
        select(Usuario).where(Usuario.correo==dto.correo, Usuario.estado_id==1)
    ).first()
    if not dato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (no existe el correo)"
        )
    #crear un token y una url
    token = f"{uuid.uuid4()}{int(time.time())}{uuid.uuid4()}"
    url = f"{os.getenv('BASE_URL_FRONTEND')}/recovery/update/{token}"
    #actualizamos el token en la tabla usuario
    try:
        dato.token = token
        session.commit()
        session.refresh(dato)

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error inesperado (error en la bd)"
        )
    #crear el mensaje en la cola SQS
    #generamos un MessageGroupId único
    message_group_id = str(int(time.time()))
    try:
        if os.getenv('ENVIRONMENT')=="local":
            sqs_client.send_message(
                QueueUrl=os.getenv('SQS_ENVIO_CORREO'),
                MessageBody=url,
                MessageAttributes={
                    'Nombre':{
                        'DataType': 'String',
                        'StringValue': dato.nombre
                    },
                    'Token':{
                        'DataType': 'String',
                        'StringValue': token
                    }
                }
            )
        else:
            sqs_client.send_message(
                QueueUrl=os.getenv('SQS_ENVIO_CORREO'),
                MessageBody=url,
                MessageAttributes={
                    'Nombre':{
                        'DataType': 'String',
                        'StringValue': dato.nombre
                    },
                    'Token':{
                        'DataType': 'String',
                        'StringValue': token
                    }
                },
                MessageGroupId=message_group_id,
                MessageDeduplicationId=str(uuid.uuid4())
            )
        return GenericInterface(estado="ok", mensaje="Se modifica el registro exitosamente")
    except ClientError as ce:
        error_code = ce.response['Error']['Code']
        error_msg = ce.response['Error']['Message']
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ocurrió un error inesperado | error_code={error_code} | error_msg={error_msg}"
        ) 