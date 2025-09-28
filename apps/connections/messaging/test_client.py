#!/usr/bin/env python3
"""
Cliente de pruebas para el servidor gRPC de Messaging.

Este cliente verifica que todas las funcionalidades del servidor estén
funcionando correctamente, incluyendo:
- Obtención de parámetros de messaging
- Obtención de routing keys
- Streaming de mensajes de schemas
- Streaming de mensajes de validation

Uso:
    python test_client.py [--host HOST] [--port PORT] [--timeout SECONDS]
"""

import argparse
import asyncio
import signal
import sys

import grpc
from messaging_utils.messaging.connection_factory import (
    RabbitMQConnectionFactory,
)
from messaging_utils.messaging.publishers import Publisher
from messaging_utils.schemas.connection import ConnectionParams
from proto_utils.generated.messaging import messaging_pb2, messaging_pb2_grpc
from proto_utils.messaging.dtypes import JsonSchema, Metadata

from src.core.config import settings


class MessagingTestClient:
    """Cliente de pruebas para el servidor gRPC de Messaging."""

    def __init__(self, host: str = "localhost", port: int = 50055):
        """
        Inicializar el cliente de pruebas.

        Args:
            host: Dirección del servidor gRPC
            port: Puerto del servidor gRPC
        """
        self.address = f"{host}:{port}"
        self.channel = None
        self.stub = None
        self.publisher = None

    async def connect(self) -> None:
        """Establecer conexión con el servidor gRPC."""
        print(f"🔌 Conectando al servidor gRPC en {self.address}...")
        self.channel = grpc.aio.insecure_channel(self.address)
        self.stub = messaging_pb2_grpc.MessagingServiceStub(self.channel)

        # Verificar que el servidor esté disponible
        try:
            await self.channel.channel_ready()
            print("✅ Conexión establecida exitosamente")
        except Exception as e:
            print(f"❌ Error al conectar con el servidor: {e}")
            raise

    async def setup_publisher(self) -> None:
        """Configurar el publisher para enviar mensajes de prueba."""
        print("📡 Configurando publisher para mensajes de prueba...")

        try:
            # Primero obtenemos los parámetros de messaging del servidor
            request = messaging_pb2.GetMessagingParamsRequest()
            response = await self.stub.GetMessagingParams(request)

            # Configuramos RabbitMQ con los parámetros obtenidos
            messaging_params = {
                "host": response.host,
                "port": response.port,
                "username": response.username,
                "password": response.password,
                "virtual_host": response.virtual_host,
                "exchange": {
                    "exchange": response.exchange.exchange,
                    "type": response.exchange.type,
                    "durable": response.exchange.durable,
                    "queues": [],
                },
            }

            RabbitMQConnectionFactory.configure(messaging_params)

            # Crear publisher
            connection_params = ConnectionParams(
                host=response.host,
                port=response.port,
                virtual_host=response.virtual_host,
                username=response.username,
                password=response.password,
            )

            exchange_info = {
                "exchange": response.exchange.exchange,
                "type": response.exchange.type,
                "durable": response.exchange.durable,
            }

            self.publisher = Publisher(
                params=connection_params, exchange_info=exchange_info
            )

            print("✅ Publisher configurado exitosamente")

        except Exception as e:
            print(f"❌ Error configurando publisher: {e}")
            raise

    async def test_get_messaging_params(self) -> None:
        """Probar la obtención de parámetros de messaging."""
        print("\n🧪 Prueba: GetMessagingParams")
        print("-" * 40)

        try:
            request = messaging_pb2.GetMessagingParamsRequest()
            response = await self.stub.GetMessagingParams(request)

            print(f"✅ Host: {response.host}")
            print(f"✅ Port: {response.port}")
            print(f"✅ Virtual Host: {response.virtual_host}")
            print(f"✅ Exchange: {response.exchange.exchange}")
            print(f"✅ Exchange Type: {response.exchange.type}")

        except Exception as e:
            print(f"❌ Error: {e}")
            raise

    async def test_get_routing_keys(self) -> None:
        """Probar la obtención de routing keys."""
        print("\n🧪 Prueba: Routing Keys")
        print("-" * 40)

        try:
            # Test schemas routing key
            schemas_request = messaging_pb2.GetRoutingKeySchemasRequest(
                results=True
            )
            schemas_response = await self.stub.GetRoutingKeySchemas(
                schemas_request
            )
            print(f"✅ Schemas routing key: {schemas_response.routing_key}")

            # Test validations routing key
            validations_request = messaging_pb2.GetRoutingKeyValidationsRequest(
                results=True
            )
            validations_response = await self.stub.GetRoutingKeyValidations(
                validations_request
            )
            print(
                f"✅ Validations routing key: {validations_response.routing_key}"
            )

        except Exception as e:
            print(f"❌ Error: {e}")
            raise

    async def test_schema_streaming(self, timeout: int = 30) -> None:
        """Probar el streaming de mensajes de schemas."""
        print(f"\n🧪 Prueba: Schema Messages Streaming (timeout: {timeout}s)")
        print("-" * 40)

        # Crear tarea para enviar mensajes de prueba
        send_task = asyncio.create_task(self._send_schema_messages())

        try:
            request = messaging_pb2.SchemaMessageRequest()

            print("📥 Iniciando streaming de mensajes de schemas...")
            messages_received = 0

            # Configurar timeout
            async def stream_with_timeout():
                async for message in self.stub.StreamSchemaMessages(request):
                    nonlocal messages_received
                    messages_received += 1
                    print(
                        f"✅ Schema message #{messages_received}: {message.id}"
                    )
                    print(f"   📄 Import name: {message.import_name}")

                    # Para la demo, paramos después de recibir algunos mensajes
                    if messages_received >= 3:
                        break

            try:
                await asyncio.wait_for(stream_with_timeout(), timeout=timeout)
                print(
                    f"✅ Streaming completado. Mensajes recibidos: {messages_received}"
                )
            except asyncio.TimeoutError:
                print(
                    f"⏰ Timeout después de {timeout}s. Mensajes recibidos: {messages_received}"
                )

        except Exception as e:
            print(f"❌ Error en streaming: {e}")
        finally:
            send_task.cancel()

    async def test_validation_streaming(self, timeout: int = 30) -> None:
        """Probar el streaming de mensajes de validation."""
        print(
            f"\n🧪 Prueba: Validation Messages Streaming (timeout: {timeout}s)"
        )
        print("-" * 40)

        # Crear tarea para enviar mensajes de prueba
        send_task = asyncio.create_task(self._send_validation_messages())

        try:
            request = messaging_pb2.ValidationMessageRequest()

            print("📥 Iniciando streaming de mensajes de validation...")
            messages_received = 0

            # Configurar timeout
            async def stream_with_timeout():
                async for message in self.stub.StreamValidationMessages(
                    request
                ):
                    nonlocal messages_received
                    messages_received += 1
                    print(
                        f"✅ Validation message #{messages_received}: {message.id}"
                    )
                    print(f"   📄 Import name: {message.import_name}")
                    print(f"   🏷️ Task: {message.task}")
                    print(f"   📁 Filename: {message.metadata.filename}")

                    # Para la demo, paramos después de recibir algunos mensajes
                    if messages_received >= 3:
                        break

            try:
                await asyncio.wait_for(stream_with_timeout(), timeout=timeout)
                print(
                    f"✅ Streaming completado. Mensajes recibidos: {messages_received}"
                )
            except asyncio.TimeoutError:
                print(
                    f"⏰ Timeout después de {timeout}s. Mensajes recibidos: {messages_received}"
                )

        except Exception as e:
            print(f"❌ Error en streaming: {e}")
        finally:
            send_task.cancel()

    async def _send_schema_messages(self) -> None:
        """Enviar mensajes de schema para probar el streaming."""
        if not self.publisher:
            return

        await asyncio.sleep(2)  # Esperar a que el streaming inicie

        for i in range(5):
            try:
                test_schema = JsonSchema(
                    schema="https://json-schema.org/draft/2020-12/schema",
                    type="object",
                    properties={
                        f"field_{i}": {"type": "string"},
                        "id": {"type": "integer"},
                    },
                    required=[f"field_{i}"],
                )

                self.publisher.publish_schema_update(
                    routing_key=settings.RABBITMQ_ROUTING_KEY_SCHEMAS,
                    schema=test_schema,
                    import_name=f"test_schema_{i}",
                    raw=False,
                    task="upload_schema",
                )

                print(f"📤 Enviado schema message #{i + 1}")
                await asyncio.sleep(2)

            except Exception as e:
                print(f"❌ Error enviando schema message: {e}")
                break

    async def _send_validation_messages(self) -> None:
        """Enviar mensajes de validation para probar el streaming."""
        if not self.publisher:
            return

        await asyncio.sleep(2)  # Esperar a que el streaming inicie

        for i in range(5):
            try:
                test_data = f"test data content {i}".encode()

                metadata = Metadata(
                    filename=f"test_file_{i}.txt",
                    content_type="text/plain",
                    size=len(test_data),
                )

                self.publisher.publish_validation_request(
                    routing_key=settings.RABBITMQ_ROUTING_KEY_VALIDATIONS,
                    file_data=test_data,
                    import_name=f"test_validation_{i}",
                    metadata=metadata,
                    task="sample_validation",
                )

                print(f"📤 Enviado validation message #{i + 1}")
                await asyncio.sleep(2)

            except Exception as e:
                print(f"❌ Error enviando validation message: {e}")
                break

    async def run_tests(self, timeout: int = 30) -> None:
        """Ejecutar todas las pruebas."""
        print("🚀 Iniciando pruebas del cliente gRPC de Messaging")
        print("=" * 60)

        try:
            await self.connect()
            await self.test_get_messaging_params()
            await self.setup_publisher()
            await self.test_get_routing_keys()
            await self.test_schema_streaming(timeout)
            await self.test_validation_streaming(timeout)

            print("\n🎉 Todas las pruebas completadas exitosamente!")

        except Exception as e:
            print(f"\n💥 Error durante las pruebas: {e}")
            sys.exit(1)
        finally:
            await self.close()

    async def close(self) -> None:
        """Cerrar conexiones."""
        if self.channel:
            await self.channel.close()
        if self.publisher:
            self.publisher.close()


def signal_handler(signum, frame):
    """Manejar señales de interrupción."""
    print(f"\n🛑 Señal recibida ({signum}). Cerrando cliente...")
    sys.exit(0)


async def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Cliente de pruebas para servidor gRPC de Messaging"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Dirección del servidor (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=50055,
        help="Puerto del servidor (default: 50051)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout para streaming en segundos (default: 30)",
    )

    args = parser.parse_args()

    # Configurar manejo de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Ejecutar pruebas
    client = MessagingTestClient(args.host, args.port)
    await client.run_tests(args.timeout)


if __name__ == "__main__":
    asyncio.run(main())
