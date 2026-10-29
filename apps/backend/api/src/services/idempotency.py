import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional

import grpc
from fastapi import UploadFile
from messaging_utils.core.config import settings as mq_settings
from messaging_utils.messaging.publishers import Publisher
from messaging_utils.schemas import Metadata
from pika.exceptions import AMQPError
from proto_utils.database import dtypes
from proto_utils.database.base_client import DatabaseClient
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from src import models, schemas
from src.core.config import settings
from src.core.constants import INSERTION_TASK, VALIDATION_TASK
from src.core.domain import get_import_name
from src.exceptions import (
    AppException,
    ContentTypeEmptyException,
    FileContentEmptyException,
    FilenameEmptyException,
    ProjectNotFoundException,
)
from src.repositories import ProjectRepository, UploadRepository
from src.utils import logger, utc_now


class IdempotencyService:
    def __init__(self, *, db: Session) -> None:
        self.upload_repository = UploadRepository(db=db)

    @staticmethod
    def _generate_idempotency_key(
        user_id: str,
        project_id: str,
        table_name: str,
        file_hash: str,
        metadata: Optional[str] = None,
        current_timestamp: Optional[datetime] = None,
    ) -> str:
        """Generate deterministic idempotency key from file and context."""
        if current_timestamp is None:
            current_timestamp = utc_now()

        data = f"{user_id}:{project_id}:{table_name}:{file_hash}"
        if metadata:
            data += f":{metadata}"

        return hashlib.sha256(data.encode()).hexdigest()

    def get_task_by_id(self, *, task_id: str) -> Optional[models.UploadTask]:
        return self.upload_repository.get_upload_task_by_id(task_id=task_id)

    def update_task_status(
        self,
        *,
        task_id: Optional[str] = None,
        status: models.TaskStatus,
        db_obj: Optional[models.UploadTask] = None,
    ) -> Optional[models.UploadTask]:
        try:
            obj = self.upload_repository.update_upload_task_status(
                task_id=task_id, status=status, db_obj=db_obj
            )
            self.upload_repository.db.commit()
        except Exception as e:
            self.upload_repository.db.rollback()
            logger.error(f"Failed to update task status for task_id={task_id}: {e}")
            raise AppException() from e

        return obj

    async def validate_task(
        self,
        db_client: DatabaseClient,
        publisher: Publisher,
        *,
        spreadsheet_file: UploadFile,
        user_id: str,
        project_id: str,
        table_name: str,
        trace_headers: Optional[schemas.OpenTelemetryTraceHeaders] = None,
    ) -> dtypes.ApiResponse:
        if not ProjectRepository(db=self.upload_repository.db).get_project_by_id(
            project_id=project_id
        ):
            raise ProjectNotFoundException()

        file_content = await spreadsheet_file.read()
        if not file_content:
            raise FileContentEmptyException()

        if not spreadsheet_file.filename:
            raise FilenameEmptyException()

        if not spreadsheet_file.content_type:
            raise ContentTypeEmptyException()

        file_hash = hashlib.sha256(file_content).hexdigest()
        idempotency_key = self._generate_idempotency_key(
            user_id=user_id,
            project_id=project_id,
            table_name=table_name,
            file_hash=file_hash,
            metadata=VALIDATION_TASK,
        )

        task_id = str(uuid.uuid4())

        # Create Metadata object obtained from the uploaded file
        metadata = Metadata(
            filename=spreadsheet_file.filename,
            content_type=spreadsheet_file.content_type,
            size=len(file_content),
        )

        # First, create the task in database with status "pending"
        try:
            db_task = self.upload_repository.create_upload_task(
                upload_task_create=schemas.UploadTaskCreateSchema(
                    task_id=task_id,
                    idempotency_key=idempotency_key,
                    status=models.TaskStatus.PENDING,
                    user_id=user_id,
                    project_id=project_id,
                    file_hash=file_hash,
                    task_metadata=metadata,
                ),
                locked_until=(
                    utc_now()
                    + timedelta(seconds=settings.IDEMPOTENCY_TTL_DEFAULT_SECONDS)
                ),
            )

            self.upload_repository.db.commit()
        except IntegrityError as e:
            self.upload_repository.db.rollback()
            if "uq_idempotency_key_active_window" in str(e.orig):
                logger.error(
                    "Idempotency key already exists for an active task, returning existing task"
                )
                existing_task = self.upload_repository.check_idempotency_task(
                    idempotency_key=idempotency_key,
                    user_id=user_id,
                    project_id=project_id,
                    statuses=[
                        models.TaskStatus.PENDING,
                        models.TaskStatus.PUBLISHED,
                    ],
                )
                if existing_task:
                    return dtypes.ApiResponse(
                        status=existing_task.status.value,
                        code=202,  # Still processing
                        message="This validation is already in progress",
                        data={
                            "task_id": str(existing_task.task_id),
                            "project_id": project_id,
                            "idempotency_key": idempotency_key,
                        },
                    )
            else:
                logger.error("Database integrity error during task creation", e)
            raise AppException() from e
        except OperationalError as e:
            # If the problem is the postgres database, roll back the transaction and raise an AppException.
            logger.error("Database operation failed, rolling back task creation", e)
            self.upload_repository.db.rollback()
            raise AppException() from e

        except Exception as e:
            logger.error("Failed to create upload task, rolling back", e)
            self.upload_repository.db.rollback()
            raise AppException() from e

        # Second, publish the task to rabbitmq broker
        try:
            # Update the status to published
            db_task.status = models.TaskStatus.PUBLISHED  # type: ignore
            db_task.locked_until = utc_now() + timedelta(  # type: ignore
                seconds=settings.IDEMPOTENCY_TTL_PUBLISHED_SECONDS
            )

            # Prepare trace headers (empty dict if not provided)
            trace_context: schemas.OpenTelemetryTraceHeaders = (
                trace_headers if trace_headers is not None else {}
            )

            # Publish in RabbitMQ
            publisher.publish_validation_request(
                routing_key=mq_settings.RABBITMQ_PUBLISHERS_ROUTING_KEY_VALIDATIONS,
                file_data=file_content,
                project_id=project_id,
                table_name=table_name,
                metadata=metadata,
                task="sample_validation",
                task_id=task_id,
                idempotency_key=idempotency_key,
                traceparent=trace_context.get("traceparent"),
                tracestate=trace_context.get("tracestate"),
                baggage=trace_context.get("baggage"),
            )

            self.upload_repository.db.commit()
        except OperationalError as e:
            logger.error("Database operation failed, rolling back task creation", e)
            self.upload_repository.db.rollback()
            raise AppException() from e
        except AMQPError as e:
            logger.error(
                "Failed to publish validation request, rolling back task creation", e
            )

            db_task.status = models.TaskStatus.PENDING  # type: ignore
            db_task.locked_until = utc_now() + timedelta(  # type: ignore
                seconds=settings.IDEMPOTENCY_TTL_RETRY_DELAY_SECONDS
            )
            self.upload_repository.db.commit()

            # The rabbitmq_exception_handler manages this error, so we can just raise the same error
            raise
        except Exception as e:
            logger.error(
                "Failed to publish validation request, rolling back task creation", e
            )
            raise AppException() from e

        # Update cache (not critical, best effort)
        try:
            await db_client.set_task_id_async(
                dtypes.SetTaskIdRequest(
                    task_id=task_id,
                    value=dtypes.ApiResponse(
                        status=models.TaskStatus.PUBLISHED.value,
                        code=202,
                        message="Validation request published successfully",
                        data={
                            "task_id": task_id,
                            "project_id": project_id,
                            "import_name": get_import_name(
                                project_id=project_id, table_name=table_name
                            ),
                        },
                    ),
                    task=VALIDATION_TASK,
                )
            )
        except grpc.RpcError as redis_err:
            # Redis/gRPC failed, but DB is already updated
            # Log and continue (Redis is cache, not critical)
            logger.error(f"Warning: Failed to update cache: {redis_err}")

        return dtypes.ApiResponse(
            status="accepted",
            code=202,
            message="Validation request published successfully",
            data={"task_id": task_id, "project_id": project_id},
        )

    async def insert_task(
        self,
        db_client: DatabaseClient,
        publisher: Publisher,
        *,
        spreadsheet_file: UploadFile,
        user_id: str,
        project_id: str,
        table_name: str,
        db_uri: str,
        overwrite: bool = False,
        trace_headers: Optional[schemas.OpenTelemetryTraceHeaders] = None,
    ) -> dtypes.ApiResponse:
        if not ProjectRepository(db=self.upload_repository.db).get_project_by_id(
            project_id=project_id
        ):
            raise ProjectNotFoundException()

        file_content = await spreadsheet_file.read()
        if not file_content:
            raise FileContentEmptyException()

        if not spreadsheet_file.filename:
            raise FilenameEmptyException()

        if not spreadsheet_file.content_type:
            raise ContentTypeEmptyException()

        file_hash = hashlib.sha256(file_content).hexdigest()
        idempotency_key = self._generate_idempotency_key(
            user_id=user_id,
            project_id=project_id,
            table_name=table_name,
            file_hash=file_hash,
            metadata=INSERTION_TASK,
        )

        task_id = str(uuid.uuid4())

        metadata = Metadata(
            filename=spreadsheet_file.filename,
            content_type=spreadsheet_file.content_type,
            size=len(file_content),
        )

        # First, create the task in database with status "pending"
        try:
            db_task = self.upload_repository.create_upload_task(
                upload_task_create=schemas.UploadTaskCreateSchema(
                    task_id=task_id,
                    idempotency_key=idempotency_key,
                    status=models.TaskStatus.PENDING,
                    user_id=user_id,
                    project_id=project_id,
                    file_hash=file_hash,
                    task_metadata=metadata,
                ),
                locked_until=(
                    utc_now()
                    + timedelta(seconds=settings.IDEMPOTENCY_TTL_DEFAULT_SECONDS)
                ),
            )

            self.upload_repository.db.commit()
        except IntegrityError as e:
            self.upload_repository.db.rollback()
            if "uq_idempotency_key_active_window" in str(e.orig):
                logger.error(
                    "Idempotency key already exists for an active task, returning existing task"
                )
                existing_task = self.upload_repository.check_idempotency_task(
                    idempotency_key=idempotency_key,
                    user_id=user_id,
                    project_id=project_id,
                    statuses=[
                        models.TaskStatus.PENDING,
                        models.TaskStatus.PUBLISHED,
                    ],
                )
                if existing_task:
                    return dtypes.ApiResponse(
                        status=existing_task.status.value,
                        code=202,  # Still processing
                        message="This insertion is already in progress",
                        data={
                            "task_id": str(existing_task.task_id),
                            "project_id": project_id,
                            "idempotency_key": idempotency_key,
                        },
                    )
        except OperationalError as e:
            logger.error("Database operation failed, rolling back task creation", e)
            self.upload_repository.db.rollback()
            raise AppException() from e

        except Exception as e:
            logger.error("Failed to create upload task, rolling back", e)
            self.upload_repository.db.rollback()
            raise AppException() from e

        # Second, publish the task to rabbitmq broker
        try:
            # Update the status to published
            db_task.status = models.TaskStatus.PUBLISHED  # type: ignore
            db_task.locked_until = utc_now() + timedelta(  # type: ignore
                seconds=settings.IDEMPOTENCY_TTL_PUBLISHED_SECONDS
            )

            # Prepare trace headers (empty dict if not provided)
            trace_context: schemas.OpenTelemetryTraceHeaders = (
                trace_headers if trace_headers is not None else {}
            )

            # Publish in RabbitMQ
            publisher.publish_insertion_request(
                routing_key=mq_settings.RABBITMQ_PUBLISHERS_ROUTING_KEY_INSERTION,
                file_data=file_content,
                project_id=project_id,
                table_name=table_name,
                scheme=str(project_id),
                metadata=metadata,
                task="sample_insertion",
                overwrite=overwrite,
                db_uri=db_uri,
                task_id=task_id,
                idempotency_key=idempotency_key,
                traceparent=trace_context.get("traceparent"),
                tracestate=trace_context.get("tracestate"),
                baggage=trace_context.get("baggage"),
            )

            self.upload_repository.db.commit()
        except OperationalError as e:
            logger.error("Database operation failed, rolling back task creation", e)
            self.upload_repository.db.rollback()
            raise AppException() from e
        except AMQPError as e:
            logger.error(
                "Failed to publish insertion request, rolling back task creation", e
            )

            db_task.status = models.TaskStatus.PENDING  # type: ignore
            db_task.locked_until = utc_now() + timedelta(  # type: ignore
                seconds=settings.IDEMPOTENCY_TTL_RETRY_DELAY_SECONDS
            )
            self.upload_repository.db.commit()

            # The rabbitmq_exception_handler manages this error, so we can just raise the same error
            raise
        except Exception as e:
            logger.error(
                "Failed to publish insertion request, rolling back task creation", e
            )
            raise AppException() from e

        # Update cache (not critical, best effort)
        try:
            await db_client.set_task_id_async(
                dtypes.SetTaskIdRequest(
                    task_id=task_id,
                    value=dtypes.ApiResponse(
                        status=models.TaskStatus.PUBLISHED.value,
                        code=202,
                        message="Insertion request published successfully",
                        data={
                            "task_id": task_id,
                            "project_id": project_id,
                            "import_name": get_import_name(
                                project_id=project_id, table_name=table_name
                            ),
                        },
                    ),
                    task=INSERTION_TASK,
                )
            )
        except grpc.RpcError as redis_err:
            # Redis/gRPC failed, but DB is already updated
            # Log and continue (Redis is cache, not critical)
            logger.error(f"Warning: Failed to update cache: {redis_err}")

        return dtypes.ApiResponse(
            status="accepted",
            code=202,
            message="Insertion request published successfully",
            data={"task_id": task_id, "project_id": project_id},
        )

    async def process_task(
        self,
        db_client: DatabaseClient,
        publisher: Publisher,
        *,
        spreadsheet_file: UploadFile,
        user_id: str,
        project_id: str,
        table_name: str,
        db_uri: str,
        overwrite: bool = False,
        trace_headers: Optional[schemas.OpenTelemetryTraceHeaders] = None,
    ) -> dtypes.ApiResponse:
        if not ProjectRepository(db=self.upload_repository.db).get_project_by_id(
            project_id=project_id
        ):
            raise ProjectNotFoundException()

        file_content = await spreadsheet_file.read()
        if not file_content:
            raise FileContentEmptyException()

        if not spreadsheet_file.filename:
            raise FilenameEmptyException()

        if not spreadsheet_file.content_type:
            raise ContentTypeEmptyException()

        file_hash = hashlib.sha256(file_content).hexdigest()
        idempotency_key = self._generate_idempotency_key(
            user_id=user_id,
            project_id=project_id,
            table_name=table_name,
            file_hash=file_hash,
            metadata=f"{VALIDATION_TASK}&{INSERTION_TASK}",
        )

        task_id = str(uuid.uuid4())
        metadata = Metadata(
            filename=spreadsheet_file.filename,
            content_type=spreadsheet_file.content_type,
            size=len(file_content),
        )

        # First, create the task in database with status "pending"
        try:
            db_task = self.upload_repository.create_upload_task(
                upload_task_create=schemas.UploadTaskCreateSchema(
                    task_id=task_id,
                    idempotency_key=idempotency_key,
                    status=models.TaskStatus.PENDING,
                    user_id=user_id,
                    project_id=project_id,
                    file_hash=file_hash,
                    task_metadata=metadata,
                ),
                locked_until=(
                    utc_now()
                    + timedelta(seconds=settings.IDEMPOTENCY_TTL_DEFAULT_SECONDS)
                ),
            )

            self.upload_repository.db.commit()
        except IntegrityError as e:
            self.upload_repository.db.rollback()
            if "uq_idempotency_key_active_window" in str(e.orig):
                logger.error(
                    "Idempotency key already exists for an active task, returning existing task"
                )
                existing_task = self.upload_repository.check_idempotency_task(
                    idempotency_key=idempotency_key,
                    user_id=user_id,
                    project_id=project_id,
                    statuses=[
                        models.TaskStatus.PENDING,
                        models.TaskStatus.PUBLISHED,
                    ],
                )
                if existing_task:
                    return dtypes.ApiResponse(
                        status=existing_task.status.value,
                        code=202,  # Still processing
                        message="This validation/insertion is already in progress",
                        data={
                            "task_id": str(existing_task.task_id),
                            "project_id": project_id,
                            "idempotency_key": idempotency_key,
                        },
                    )
        except OperationalError as e:
            logger.error("Database operation failed, rolling back task creation", e)
            self.upload_repository.db.rollback()
            raise AppException() from e

        except Exception as e:
            logger.error("Failed to create upload task, rolling back", e)
            self.upload_repository.db.rollback()
            raise AppException() from e

        # Second, publish the task to rabbitmq broker
        try:
            # Update the status to published
            db_task.status = models.TaskStatus.PUBLISHED  # type: ignore
            db_task.locked_until = utc_now() + timedelta(  # type: ignore
                seconds=settings.IDEMPOTENCY_TTL_PUBLISHED_SECONDS
            )

            # Prepare trace headers (empty dict if not provided)
            trace_context: schemas.OpenTelemetryTraceHeaders = (
                trace_headers if trace_headers is not None else {}
            )

            # Publish in RabbitMQ
            publisher.publish_validation_request(
                routing_key=mq_settings.RABBITMQ_PUBLISHERS_ROUTING_KEY_VALIDATIONS,
                file_data=file_content,
                project_id=project_id,
                table_name=table_name,
                metadata=metadata,
                task="sample_validation",
                insert=True,
                insert_overwrite=overwrite,
                insert_scheme=str(project_id),
                insert_db_uri=db_uri,
                task_id=task_id,
                idempotency_key=idempotency_key,
                traceparent=trace_context.get("traceparent"),
                tracestate=trace_context.get("tracestate"),
                baggage=trace_context.get("baggage"),
            )

            self.upload_repository.db.commit()
        except OperationalError as e:
            logger.error("Database operation failed, rolling back task creation", e)
            self.upload_repository.db.rollback()
            raise AppException() from e
        except AMQPError as e:
            logger.error(
                "Failed to publish validation/insertion request, rolling back task creation",
                e,
            )

            db_task.status = models.TaskStatus.PENDING  # type: ignore
            db_task.locked_until = utc_now() + timedelta(  # type: ignore
                seconds=settings.IDEMPOTENCY_TTL_RETRY_DELAY_SECONDS
            )
            self.upload_repository.db.commit()

            # The rabbitmq_exception_handler manages this error, so we can just raise the same error
            raise
        except Exception as e:
            logger.error(
                "Failed to publish validation/insertion request, rolling back task creation",
                e,
            )
            raise AppException() from e

        # Update cache (not critical, best effort)
        try:
            await db_client.set_task_id_async(
                dtypes.SetTaskIdRequest(
                    task_id=task_id,
                    value=dtypes.ApiResponse(
                        status=models.TaskStatus.PUBLISHED.value,
                        code=202,
                        message="Validation/Insertion request published successfully",
                        data={
                            "task_id": task_id,
                            "project_id": project_id,
                            "import_name": get_import_name(
                                project_id=project_id, table_name=table_name
                            ),
                        },
                    ),
                    task=VALIDATION_TASK,
                )
            )
        except grpc.RpcError as redis_err:
            # Redis/gRPC failed, but DB is already updated
            # Log and continue (Redis is cache, not critical)
            logger.error(f"Warning: Failed to update cache: {redis_err}")

        return dtypes.ApiResponse(
            status="accepted",
            code=202,
            message="Validation/Insertion request published successfully",
            data={"task_id": task_id, "project_id": project_id},
        )
