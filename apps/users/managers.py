from django.contrib.auth.base_user import BaseUserManager

from apps.core.exceptions import (
    NoneExistenceError,
    PreExistenceError,
    PreviousValueMatchingError,
)
from configs.definitions import DEBUG


class CustomUserManager(BaseUserManager):
    """
    Custom function for creating users i.e. user manager using djangos BaseUserManager
    """

    def _create_user(
        self,
        username: str,
        email: str,
        password: str,
        is_email_verified: bool,
        **extra_fields,
    ):
        """
        Creates and saves a User with given fields
        """
        if not username:
            raise ValueError("username is mandatory")
        if not email:
            raise ValueError("Email is mandatory")
        if not password:
            raise ValueError("Password is mandatory")

        email = self.normalize_email(email)
        new_user = self.model(email=email, username=username)
        new_user.set_password(password)
        new_user.email_verified = is_email_verified

        new_user.admin = extra_fields["is_superuser"]
        new_user.staff = extra_fields["is_staff"]
        new_user.active = extra_fields["is_active"]

        new_user.save(using=self._db)
        if DEBUG:
            print("SUCCESS: New User Created!")

        return new_user

    def _check_required_fields(self, **req_fields):
        """
        Checks required fields
        """

        if not req_fields["username"]:
            raise ValueError("username is mandatory")
        if not req_fields["email"]:
            raise ValueError("Email is mandatory")
        if not req_fields["password"]:
            raise ValueError("Password is mandatory")

    def _check_extra_fields(self, **extra_fields):
        """
        Checks the extra fields
        """
        keys_valuestype = {
            "is_active": bool(),
            "is_staff": bool(),
            "is_superuser": bool(),
        }
        # check missing keys
        diff = set(keys_valuestype) - set(extra_fields)
        if len(diff) != 0:
            raise ValueError(
                f"Missing Fields: The following fields are missing: {diff} "
            )

        # check unnecessary fields
        unnecessary = set(extra_fields) - set(keys_valuestype)
        if len(unnecessary) != 0:
            raise KeyError(
                f"Unnecessary Fields: The following fields are unnecessary: \t{unnecessary}"
            )

        # check type of entered values
        for key, value in extra_fields.items():
            if not isinstance(value, type(keys_valuestype[key])):
                raise TypeError(
                    f"{key} must have value of type '{type(keys_valuestype[key]).__name__}'"
                )

        return True

    def create_user(self, username, email, password, **extra_fields):
        """
        Creates a regular user
        """
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        if self._check_extra_fields(**extra_fields):
            return self._create_user(username, email, password, False, **extra_fields)

    def create_staffuser(self, username, email, password, **extra_fields):
        """
        Creates a is_staff user
        """
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)

        if self._check_extra_fields(**extra_fields):
            return self._create_user(username, email, password, False, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        """
        Creates a super user
        """
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if self._check_extra_fields(**extra_fields):
            return self._create_user(username, email, password, False, **extra_fields)

    def update_user(self, userid, **fields):
        """
        Updates user account details like username

        Note
        """
        try:

            if DEBUG:
                print("update_user")

            field_options = ["username", "email", "password", "active"]
            included = list()
            for key, value in fields.items():
                if key in field_options:
                    included.append(key)

            if len(included) == 0:
                raise KeyError("No keys provided!")

            new_username = fields.get("username", False)
            new_email = fields.get("email", False)
            new_password = fields.get("password", False)
            new_active = fields.get("active", False)

            user_to_update = super().get(pk=userid)

            if not user_to_update:
                raise NoneExistenceError(
                    instance=userid,
                    message={
                        "status": 400,
                        "error": {
                            "message": "Non Existence",
                            "detail": f"Provided userid credentials to `update_user` does not match any users",
                        },
                    },
                )

            if new_username:
                if super().filter(username=new_username).exists():
                    raise PreExistenceError(
                        instance=new_username,
                        message={
                            "status": 400,
                            "error": {
                                "message": "Already Exists",
                                "detail": f'username "{new_username}" already taken. Try other username',
                            },
                        },
                    )
                if user_to_update.username != new_username:
                    user_to_update.username = new_username
                # else:
                #     raise PreviousValueMatchingError(instance="username")

            if new_email:
                new_email = self.normalize_email(new_email)
                if super().filter(email=new_email).exists():
                    raise PreExistenceError(
                        instance=new_email,
                        message={
                            "status": 400,
                            "error": {
                                "message": "Already Exists",
                                "detail": f'email "{new_email}" already taken. Try other username',
                            },
                        },
                    )
                if user_to_update.email != new_email:
                    user_to_update.email = new_email
                    user_to_update.email_verified = False
                # else:
                #     raise PreviousValueMatchingError(instance="email")

            if new_password:
                if not user_to_update.check_password(new_password):
                    user_to_update.set_password(new_password)
                # else:
                #     raise PreviousValueMatchingError(instance="passsword")

            if fields.__contains__("active"):
                if user_to_update.active != new_active:
                    user_to_update.active = new_active
                # else:
                #     raise PreviousValueMatchingError(instance="active")

            user_to_update.save()

            return user_to_update

        except (PreExistenceError, NoneExistenceError) as error:
            print(error.name, error)
            raise error

        except PreviousValueMatchingError as error:
            print(error.name, error)
            raise PreviousValueMatchingError(
                instance=error.instance,
                message={
                    "status": 400,
                    "error": {
                        "message": "Previous value matching",
                        "detail": f"Field `{error.instance}` matches the previous credential. Please provide new credentials for update",
                    },
                },
            )

        except Exception as error:
            print("Exception", error)
            raise error
