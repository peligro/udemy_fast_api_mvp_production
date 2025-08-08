
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

import boto3
from botocore.exceptions import ClientError

from utilidades.utilidades import sendMail
from models.models import Usuario
from database import engine
from sqlmodel import Session, select


def iniciar_sqs_background_task(app):
    @app.on_event("startup")
    def worker_leer_sqs():
        async def tarea_de_fondo():
            print("Worker SQS iniciado: leyendo mensajes cada 5 segundos")
            while True:
                try:
                    #configurar cliente SQS
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
                    queue_url = os.getenv('SQS_ENVIO_CORREO')
                    #leer mensajes de la cola
                    response = await asyncio.to_thread(
                        sqs_client.receive_message,
                        QueueUrl=queue_url,
                        MaxNumberOfMessages=5,
                        WaitTimeSeconds=2,
                        MessageAttributeNames=["All"]
                    )
                    messages = response.get("Messages", [])
                    if not messages:
                        await asyncio.sleep(5)
                        continue
                    for message in messages:
                        mensaje_cuerpo = message["Body"]
                        atributos= message.get("MessageAttributes", {})
                        receipt_handle = message["ReceiptHandle"]
                        
                        #enviamos el correo
                        try:
                            token = atributos.get("Token", {}).get("StringValue", "")
                            nombre_usuario= atributos.get("Nombre", {}).get("StringValue", "Usuario")
                            #consultar en la base de datos
                            with Session(engine) as session:
                                usuario = session.exec(
                                    select(Usuario).where(Usuario.token==token, Usuario.estado_id==1)
                                ).first()
                            if not usuario:
                                print(f"No se encontró usuaro con token {token} y estado_id=1")
                                #opcional: borra el mensaje si no tiene sentiro reintentarlo
                                await asyncio.to_thread(
                                    sqs_client.delete_message,
                                    QueueUrl=queue_url,
                                    ReceiptHandle= receipt_handle
                                )
                                print("mensaje eliminado (usuario no encontrado)")
                                continue

                            #envia el correo
                            html = f"""
                                <h2>Recuperación de contraseña</h2>
                                <p>Hola {usuario.nombre}</p>
                                <p>Haz clic en el siguiente enlace para restablecer tu contraseña:</p>
                                <a href="{mensaje_cuerpo}">{mensaje_cuerpo}</a>
                                <br /><br/>
                                <small>Este enlace expira en 24 horas</small>
                            """
                            sendMail(html=html, asunto="Restablece tu contraseña", para=usuario.correo)
                            await asyncio.to_thread(
                                    sqs_client.delete_message,
                                    QueueUrl=queue_url,
                                    ReceiptHandle= receipt_handle
                                )
                            print("Mensaje borrado de la cola, correo enviado!!!")
                        except Exception as e:
                            print("Error al procesar el mensaje:", e)

                except ClientError as e:
                    print("Error en conexión SQS", e)
                    await asyncio.sleep(10)
                except Exception as e2:
                    print("Error general del worker", e2)
                    await asyncio.sleep(10)
        #iniciar la tarea de fondo cuando arranque la app
        asyncio.create_task(tarea_de_fondo())
    return worker_leer_sqs


"""
def iniciar_sqs_background_task(app):
    @app.on_event("startup")
    def worker_leer_sqs():
        async def tarea_de_fondo():
            print("Worker SQS iniciado: leyendo mensajes cada 5 segundos")
            while True:
                try:
                    #configurar cliente SQS
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
                    queue_url = os.getenv('SQS_ENVIO_CORREO')
                    #leer mensajes de la cola
                    response = await asyncio.to_thread(
                        sqs_client.receive_message,
                        QueueUrl=queue_url,
                        MaxNumberOfMessages=5,
                        WaitTimeSeconds=2,
                        MessageAttributeNames=["All"]
                    )
                    messages = response.get("Messages", [])
                    if not messages:
                        await asyncio.sleep(5)
                        continue
                    for message in messages:
                        mensaje_cuerpo = message["Body"]
                        atributos= message.get("MessageAttributes", {})
                        receipt_handle = message["ReceiptHandle"]
                        print(f"Procesando mensaje con toke: {atributos.get('Token', {}).get('StringValue', '')}")
                        print("Atributos", atributos)

                except ClientError as e:
                    print("Error en conexión SQS", e)
                    await asyncio.sleep(10)
                except Exception as e2:
                    print("Error general del worker", e2)
                    await asyncio.sleep(10)
        #iniciar la tarea de fondo cuando arranque la app
        asyncio.create_task(tarea_de_fondo())
    return worker_leer_sqs
"""

"""
def iniciar_sqs_background_task(app):
    @app.on_event("startup")
    def worker_leer_sqs():
        async def tarea_de_fondo():
            print("Worker SQS iniciado: leyendo mensajes cada 5 segundos")
            pass
        asyncio.create_task(tarea_de_fondo())
    return worker_leer_sqs
"""