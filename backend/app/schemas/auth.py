from typing import Annotated

from pydantic import AfterValidator, BaseModel, EmailStr, StringConstraints


def fits_bcrypt(password: str) -> str:
    if len(password.encode()) > 72:
        raise ValueError("Password can't be longer than 72 bytes")
    return password


Email = Annotated[EmailStr, AfterValidator(str.lower)]
Password = Annotated[str, StringConstraints(min_length=8), AfterValidator(fits_bcrypt)]
FullName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)
]


class RegisterRequest(BaseModel):
    email: Email
    password: Password
    full_name: FullName


class LoginRequest(BaseModel):
    email: Email
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
