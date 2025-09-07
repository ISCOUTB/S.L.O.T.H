import datetime

import src.models as models
import src.schemas as schemas
from src.controllers.utils import (
    validate_unique_fields,
    parse_integrity_error,
    valid_email_format,
    valid_phone_format,
)
from src.core.security import verify_password, get_password_hash

import sqlalchemy.exc
from sqlalchemy import select, Select
from sqlalchemy.orm import Session


class ControllerUsers:
    @staticmethod
    def get_user_rol(
        search_user: schemas.users.SearchUser, db: Session, active: bool = True
    ) -> models.user_roles.UserRoles | None:
        """
        Gets a user instance directly from the user roles table.

        Args:
            search_user (schemas.users.SearchUser): User search information to find in the database.
            db (Session): Database session for making queries to the sql database.
            active (bool): Limitation to only get an active user. Default is True.

        Returns:
            models.user_roles.UserRoles | None: Returns a UserRoles object if it exists, otherwise returns None.
        """
        conditions = [
            models.user_roles.UserRoles.username == search_user.username,
            models.user_roles.UserRoles.rol == search_user.rol,
        ]
        if active:
            conditions.append(models.user_roles.UserRoles.is_active)

        return db.query(models.user_roles.UserRoles).filter(*conditions).first()

    @staticmethod
    def get_user_by_username(
        username: str, db: Session, active: bool = True
    ) -> models.user_roles.UserRoles | None:
        """
        Gets a user by username from the user roles table.

        Args:
            username (str): Username of the user to find.
            db (Session): Database session for making queries to the sql database.
            active (bool): Limitation to only get an active user. Default is True.

        Returns:
            models.user_roles.UserRoles | None: Returns a UserRoles object if it exists, otherwise returns None.
        """
        conditions = [models.user_roles.UserRoles.username == username]
        if active:
            conditions.append(models.user_roles.UserRoles.is_active)

        return db.query(models.user_roles.UserRoles).filter(*conditions).first()

    @classmethod
    def authenticate_user(
        cls, user_login: schemas.users.LoginUser, db: Session
    ) -> models.user_roles.UserRoles | None:
        """
        Authenticates that the user exists in the database when logging in.

        Args:
            user_login (schemas.users.LoginUser): User login information to enter the system.
            db (Session): Database session for making queries to the sql database.

        Returns:
            models.user_roles.UserRoles | None: Returns a UserRoles object if the user was authenticated
            correctly. Otherwise returns None.
        """
        search_user = schemas.users.SearchUser(
            username=user_login.username, rol=user_login.rol
        )
        user: models.user_roles.UserRoles | None = cls.get_user_rol(search_user, db)

        if user is None:
            return None
        if not verify_password(user_login.password, user.password):
            return None

        return user

    @staticmethod
    def join_users(active: bool = True) -> Select:
        """
        Creates a SQL statement to join user information and user roles tables.

        Args:
            active (bool): Filter to only include active users. Default is True.

        Returns:
            Select: SQL select statement joining UserInfo and UserRoles tables.
        """
        stmt = select(
            models.user_info.UserInfo.username,
            models.user_info.UserInfo.name,
            models.user_info.UserInfo.surname,
            models.user_info.UserInfo.sex,
            models.user_info.UserInfo.phone,
            models.user_info.UserInfo.email,
            models.user_roles.UserRoles.rol,
            models.user_roles.UserRoles.is_active,
        ).join(
            models.user_roles.UserRoles,
            models.user_info.UserInfo.username == models.user_roles.UserRoles.username,
        )

        if active:
            stmt = stmt.where(models.user_roles.UserRoles.is_active)

        return stmt

    @classmethod
    def get_user(
        cls,
        username: str,
        db: Session,
        active: bool = True,
        rol: bool = False,
    ) -> schemas.users.AllUser | schemas.users.BaseUser | None:
        """
        Gets basic information of a system user regardless of role.

        Args:
            username (str): Username of the user to find.
            db (Session): Database session for making queries to the sql database.
            active (bool): Filter to ensure the user has at least one active role in the hospital. Default is True.
            rol (bool): Specifies if all roles of the same user should be shown.
                When rol=True, the function returns an AllUser object and BaseUser when rol=False.
                Default is False.

        Returns:
            schemas.users.AllUser | schemas.users.BaseUser | None: When rol=False the function returns BaseUser,
            when rol=True, it returns AllUser. If the user is not found, returns None.
        """
        stmt = cls.join_users(active).where(
            models.user_info.UserInfo.username == username
        )
        query = db.execute(stmt).all()
        if not query:
            return None

        base_user = schemas.users.BaseUser(
            username=query[0][0],
            name=query[0][1],
            surname=query[0][2],
            sex=query[0][3],
            phone=query[0][4],
            email=query[0][5],
        )
        if rol:
            roles: list[schemas.users.RolesInfo] = list(
                map(lambda row: {"rol": row[-2], "is_active": row[-1]}, query)
            )
            return schemas.users.AllUser(**base_user.model_dump(), roles=roles)

        return base_user

    @classmethod
    def get_users(
        cls,
        db: Session,
        *,
        active: bool = True,
        rol: bool = False,
        limit: int = 100,
        page: int = 1,
    ) -> schemas.api.Paginated[schemas.users.BaseUser | schemas.users.AllUser]:
        """
        Gets all users in the system with their basic information using pagination.

        Args:
            db (Session): Database session for making queries to the sql database.
            active (bool): Filter to ensure the user has at least one active role. Default is True.
            rol (bool): Specifies if all roles of the same user should be shown.
                When rol=True, the function returns `AllUser` objects and `BaseUser` when rol=False.
                Default is False.
            limit (int): Maximum number of users to return per page. Default is 100.
            page (int): Page number (1-based). Default is 1.

        Returns:
            schemas.api.Paginated[schemas.users.BaseUser | schemas.users.AllUser]: Dictionary containing:
                - items: List of users with their basic information
                - total: Total number of users
                - page: Current page number
                - limit: Number of users per page
                - total_pages: Total number of pages
                - has_next: Whether there's a next page
                - has_prev: Whether there's a previous page
        """
        offset = (page - 1) * limit
        stmt = cls.join_users(active)

        # Get total count
        count_stmt = select(models.user_info.UserInfo.username).join(
            models.user_roles.UserRoles,
            models.user_info.UserInfo.username == models.user_roles.UserRoles.username,
        )
        if active:
            count_stmt = count_stmt.where(models.user_roles.UserRoles.is_active)

        total = len(db.execute(count_stmt).all())
        stmt = stmt.limit(limit).offset(offset)
        query = db.execute(stmt).all()

        if not query:
            return {
                "items": [],
                "total": 0,
                "page": page,
                "limit": limit,
                "total_pages": 0,
                "has_next": False,
                "has_prev": False,
            }

        # Group users by username to handle multiple roles
        users_dict = {}
        for row in query:
            username = row[0]
            if username not in users_dict:
                users_dict[username] = {
                    "username": row[0],
                    "name": row[1],
                    "surname": row[2],
                    "sex": row[3],
                    "phone": row[4],
                    "email": row[5],
                    "roles": [],
                }

            users_dict[username]["roles"].append({"rol": row[6], "is_active": row[7]})

        # Convert to schemas
        users = []
        for user_data in users_dict.values():
            base_user = schemas.users.BaseUser(
                username=user_data["username"],
                name=user_data["name"],
                surname=user_data["surname"],
                sex=user_data["sex"],
                phone=user_data["phone"],
                email=user_data["email"],
            )

            if rol:
                users.append(
                    schemas.users.AllUser(
                        **base_user.model_dump(), roles=user_data["roles"]
                    )
                )
                continue

            users.append(base_user)

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit  # Ceiling division
        has_next = page < total_pages
        has_prev = page > 1

        return {
            "items": users,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
        }

    @classmethod
    def create_user(
        cls, new_user: schemas.users.CreateUser, db: Session, admin: bool = True
    ) -> schemas.users.Output:
        """
        Creates a new user in the system. This operation is exclusively reserved for system administrators,
        and, if wanting to add an administrator, only the superuser could perform it.

        For users that are not previously added to the system, their space will be created without problems.
        If the user with that role exists in the system as inactive, it will only change state, otherwise,
        the operation cannot be performed.

        Args:
            new_user (schemas.users.CreateUser): Information of the new user.
            db (Session): Database session for making queries to the sql database.
            admin (bool): Validates if you want to add administrator information. Default is True.

        Returns:
            schemas.users.Output: Returns a dictionary symbolizing the response status. These are the possible response states:
                - number 0: Successful response
                - number 1: User is administrator, cannot be created. Only appears when admin=False.
                - number 2: Active user with same username and role
                - number 3: User with same email
                - number 4: User with same phone number
        """
        if new_user.rol == "admin" and not admin:
            return {"number": 1, "message": "Cannot create admin user.", "status": 403}

        # Check if user already exists (without transaction)
        user: schemas.users.AllUser = cls.get_user(
            new_user.username, db, rol=True, active=False
        )

        try:
            # Create user information if not exists in the system
            if user is None:
                # Validate format first
                if new_user.email is not None and not valid_email_format(
                    new_user.email
                ):
                    return {
                        "number": 4,
                        "message": "Invalid email format.",
                        "status": 400,
                    }

                if new_user.phone is not None and not valid_phone_format(
                    new_user.phone
                ):
                    return {
                        "number": 5,
                        "message": "Invalid phone format.",
                        "status": 400,
                    }

                # Validate uniqueness in a single query
                validation_result = validate_unique_fields(
                    db, email=new_user.email, phone=new_user.phone
                )

                if not validation_result["email_valid"]:
                    return {
                        "number": 3,
                        "message": "Email already exists.",
                        "status": 409,
                    }

                if not validation_result["phone_valid"]:
                    return {
                        "number": 4,
                        "message": "Phone number already exists.",
                        "status": 409,
                    }

                user_info = models.user_info.UserInfo(
                    username=new_user.username,
                    name=new_user.name,
                    surname=new_user.surname,
                    sex=new_user.sex,
                    phone=new_user.phone,
                    email=new_user.email,
                )
                db.add(user_info)
                db.commit()

            user_rol: models.user_roles.UserRoles | None = cls.get_user_rol(
                schemas.users.SearchUser(username=new_user.username, rol=new_user.rol),
                db,
                False,
            )

            # Create user role if not exists
            if user_rol is None:
                new_user_rol = models.user_roles.UserRoles(
                    username=new_user.username,
                    rol=new_user.rol,
                    password=get_password_hash(new_user.password),
                    is_active=True,
                )
                db.add(new_user_rol)
                db.commit()
                return {
                    "number": 0,
                    "message": "User created successfully.",
                    "status": 201,
                }

            # If user role is active, return status
            if user_rol.is_active:
                return {
                    "number": 2,
                    "message": "Active user with same username and role already exists.",
                    "status": 409,
                }

            # Reactivate user
            user_rol.is_active = True
            db.commit()
            return {
                "number": 0,
                "message": "User activated successfully.",
                "status": 200,
            }

        except sqlalchemy.exc.IntegrityError as e:
            # Parse the specific constraint that was violated
            db.rollback()
            error_info = parse_integrity_error(e)
            return {
                "number": error_info["number"],
                "message": error_info["message"],
                "status": 409,
            }
        except Exception as e:
            db.rollback()
            return {
                "number": 500,
                "message": f"Unexpected error: {repr(e)}",
                "status": 500,
            }

    @classmethod
    def update_user(
        cls,
        search_user: schemas.users.SearchUser,
        updated_info: schemas.users.UpdateUser,
        db: Session,
        admin: bool = False,
    ) -> schemas.users.Output:
        """
        Updates the complete information of any user within the system regardless of their current state (active or not).

        Args:
            search_user (schemas.users.SearchUser): User search information to find in the database.
            updated_info (schemas.users.UpdateUser): Information to be updated.
            db (Session): Database session for making queries to the sql database.
            admin (bool): Validates if you want to update administrator information. Default is False.

        Returns:
            schemas.users.Output: Returns a dictionary symbolizing the response status. These are the possible response states:
                - number 0: Successful response
                - number 1: User does not exist
                - number 2: User is administrator, cannot be edited. Only appears when admin=False.
                - number 3: Username already exists (when updating username)
                - number 4: Email already exists
                - number 5: Phone number already exists
        """
        # Get the user with all roles to check if exists and if is admin (without transaction)
        user: schemas.users.AllUser = cls.get_user(
            search_user.username, db, rol=True, active=False
        )

        if user is None:
            return {"number": 1, "message": "User does not exist.", "status": 404}

        # Check if user has admin role and admin updates are not allowed
        if not admin and any(role["rol"] == "admin" for role in user.roles):
            return {
                "number": 2,
                "message": "Cannot edit administrator user.",
                "status": 403,
            }

        try:
            # Get the user info and user role objects for updating
            user_info: models.user_info.UserInfo = (
                db.query(models.user_info.UserInfo)
                .filter(models.user_info.UserInfo.username == search_user.username)
                .first()
            )

            user_rol: models.user_roles.UserRoles = cls.get_user_rol(
                search_user, db, False
            )

            # Get only the fields that are not None from updated_info
            update_data = updated_info.model_dump(exclude_unset=True, exclude_none=True)

            # Handle special validations for unique fields
            if (
                "username" in update_data
                and update_data["username"] != user_info.username
            ):
                existing_user = cls.get_user_by_username(
                    update_data["username"], db, active=False
                )
                if existing_user is not None:
                    return {
                        "number": 3,
                        "message": "Username already exists.",
                        "status": 409,
                    }

            # Validate format for email and phone
            if "email" in update_data and not valid_email_format(update_data["email"]):
                return {
                    "number": 4,
                    "message": "Invalid email format.",
                    "status": 400,
                }

            if "phone" in update_data and not valid_phone_format(update_data["phone"]):
                return {
                    "number": 5,
                    "message": "Invalid phone format.",
                    "status": 400,
                }

            # Validate uniqueness for email and phone in a single query
            fields_to_validate = {}
            if "email" in update_data and update_data["email"] != user_info.email:
                fields_to_validate["email"] = update_data["email"]
            if "phone" in update_data and update_data["phone"] != user_info.phone:
                fields_to_validate["phone"] = update_data["phone"]

            if fields_to_validate:
                validation_result = validate_unique_fields(
                    db,
                    email=fields_to_validate.get("email"),
                    phone=fields_to_validate.get("phone"),
                    exclude_username=search_user.username,
                )

                if (
                    "email" in fields_to_validate
                    and not validation_result["email_valid"]
                ):
                    return {
                        "number": 4,
                        "message": f"Email already exists. {update_data['email']}",
                        "status": 409,
                    }

                if (
                    "phone" in fields_to_validate
                    and not validation_result["phone_valid"]
                ):
                    return {
                        "number": 5,
                        "message": f"Phone number already exists. {update_data['phone']}",
                        "status": 409,
                    }

            # Update user_info fields
            user_info_fields = {
                "username",
                "name",
                "surname",
                "sex",
                "phone",
                "email",
            }
            for field, value in update_data.items():
                if field not in user_info_fields:
                    continue

                setattr(user_info, field, value)

                # If username changes, also update it in user_rol
                if field == "username":
                    setattr(user_rol, field, value)
                    # TODO: Make a call to update import_names too

            # Update user_rol specific fields
            user_rol_fields = {"password", "rol"}
            for field, value in update_data.items():
                if field in user_rol_fields:
                    if field == "password":
                        # Hash the password before storing
                        setattr(user_rol, field, get_password_hash(value))
                        continue
                    setattr(user_rol, field, value)

            db.commit()
            return {
                "number": 0,
                "message": "User updated successfully.",
                "status": 200,
            }

        except sqlalchemy.exc.IntegrityError as e:
            # Parse the specific constraint that was violated
            db.rollback()
            error_info = parse_integrity_error(e)
            return {
                "number": error_info["number"],
                "message": error_info["message"],
                "status": 409,
            }
        except Exception as e:
            db.rollback()
            return {
                "number": 500,
                "message": f"Unexpected error: {repr(e)}",
                "status": 500,
            }

    @classmethod
    def delete_user(
        cls,
        search_user: schemas.users.SearchUser,
        db: Session,
        admin: bool = False,
    ) -> schemas.users.Output:
        """
        "Deletes" an active user within the system. In reality, what is done is to set the user as inactive.

        Args:
            search_user (schemas.users.SearchUser): User search information to find in the database.
            db (Session): Database session for making queries to the sql database.
            admin (bool): Specifies if it is possible to delete an administrator within the database.
                         By default, admin=False.

        Returns:
            schemas.users.Output: Returns a dictionary symbolizing the response status. These are the possible response states:
                - number 0: Successful response
                - number 1: User does not exist
                - number 2: User is administrator, cannot be deleted. Only appears when admin=False and rol='admin'.
        """
        if search_user.rol == "admin" and not admin:
            return {
                "number": 2,
                "message": "Cannot delete administrator user.",
                "status": 403,
            }

        try:
            user: models.user_roles.UserRoles | None = cls.get_user_rol(search_user, db)

            if user is None:
                return {
                    "number": 1,
                    "message": "User does not exist.",
                    "status": 404,
                }

            user.is_active = False
            user.inactivity = datetime.date.today()
            db.commit()

            return {
                "number": 0,
                "message": "User deleted successfully.",
                "status": 200,
            }

        except sqlalchemy.exc.IntegrityError as e:
            db.rollback()
            return {
                "number": 409,
                "message": f"Cannot delete user due to database constraints: {repr(e)}",
                "status": 409,
            }
        except Exception as e:
            db.rollback()
            return {
                "number": 500,
                "message": f"Unexpected error: {repr(e)}",
                "status": 500,
            }

    @classmethod
    def delete_completely_user(
        cls,
        search_user: schemas.users.SearchUser,
        db: Session,
        admin: bool = False,
    ) -> schemas.users.Output:
        """
        Completely deletes a user from the system. This operation is exclusively reserved for system administrators,
        and, if wanting to delete an administrator, only the superuser could perform it.

        Args:
            search_user (schemas.users.SearchUser): User search information to find in the database.
            db (Session): Database session for making queries to the sql database.
            admin (bool): Specifies if it is possible to delete an administrator within the database.
                         By default, admin=False.

        Returns:
            schemas.users.Output: Returns a dictionary symbolizing the response status. These are the possible response states:
                - number 0: Successful response
                - number 1: User does not exist
                - number 2: User is administrator, cannot be deleted. Only appears when admin=False and rol='admin'.
                - number 3: User is active, cannot be deleted completely.
        """
        if search_user.rol == "admin" and not admin:
            return {
                "number": 2,
                "message": "Cannot delete administrator user.",
                "status": 403,
            }

        try:
            user: models.user_roles.UserRoles | None = cls.get_user_rol(
                search_user, db, active=False
            )

            if user is None:
                return {
                    "number": 1,
                    "message": "User does not exist.",
                    "status": 404,
                }

            if user.is_active:
                return {
                    "number": 3,
                    "message": "Cannot delete active user completely. Deactivate first.",
                    "status": 400,
                }

            db.delete(user)
            db.commit()
            return {
                "number": 0,
                "message": "User deleted completely from system.",
                "status": 200,
            }

        except sqlalchemy.exc.IntegrityError as e:
            db.rollback()
            return {
                "number": 409,
                "message": f"Cannot delete user due to foreign key constraints: {repr(e)}",
                "status": 409,
            }
        except Exception as e:
            db.rollback()
            return {
                "number": 500,
                "message": f"Unexpected error: {repr(e)}",
                "status": 500,
            }
