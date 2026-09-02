from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UserPayload(BaseModel):
    nombre: str = Field(default="Sin Nombre")
    apellido: str = Field(default="-")
    usuario: str = Field(..., min_length=1)
    depto: str = Field(default="-")
    pass_: str = Field(default="1234", alias="pass")
    rol: str = Field(default="lectura")
    requester: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class UserUpdatePayload(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    usuario: Optional[str] = None
    depto: Optional[str] = None
    rol: Optional[str] = None
    requester: Optional[str] = None


class UserOut(BaseModel):
    id: int
    nombre: str
    apellido: str
    usuario: str
    depto: str
    rol: str


class AuthResponse(BaseModel):
    message: str
    user: UserOut


class ComputerRecordPayload(BaseModel):
    serial: str = "-"
    usuario: str = "-"
    marca: str = "-"
    tipo: str = "PC"
    depto: str = "-"
    ip: str = "-"
    operativo: str = "Sí"
    puerto: str = "-"
    nota: str = "-"


class PrinterRecordPayload(BaseModel):
    serial: str = "-"
    usuario: str = "Impresora"
    marca: str = "-"
    tipo: str = "Impresora"
    depto: str = "-"
    ip: str = "-"
    operativo: str = "Sí"
    puerto: str = "-"
    nota: str = "-"


class GenericRecordPayload(BaseModel):
    serial: str = "-"
    usuario: str = "-"
    marca: str = "-"
    tipo: str = "PC"
    depto: str = "-"
    ip: str = "-"
    operativo: str = "Sí"
    puerto: str = "-"
    nota: str = "-"
