from datetime import datetime
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.config import APP_TITLE, APP_VERSION, DEBUG
from app.database import Base, SessionLocal, engine, get_db
from app.models import ComputerRecord, Department, PrinterRecord, User
from app.schemas import (
    AuthResponse,
    ComputerRecordPayload,
    GenericRecordPayload,
    LoginRequest,
    PrinterRecordPayload,
    UserOut,
    UserPayload,
    UserUpdatePayload,
)

app = FastAPI(title=APP_TITLE, version=APP_VERSION, debug=DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPER_ADMIN_USERNAME = "bsalazar"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def require_super_admin(requester_username: str | None, db: Session) -> str:
    username = (requester_username or "").strip()
    if not username:
        raise HTTPException(status_code=403, detail="Debe iniciar sesión para administrar usuarios.")
    if username.lower() == SUPER_ADMIN_USERNAME.lower():
        return username
    user = db.query(User).filter(User.username == username).first()
    if not user or (user.role or "").strip().lower() != "admin":
        raise HTTPException(status_code=403, detail="No tiene permisos de administrador.")
    return username


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def ensure_department(db: Session, name: str | None) -> Department | None:
    if not name or name.strip() == "-":
        return None
    dept = db.query(Department).filter(Department.name == name.strip()).first()
    if dept is None:
        dept = Department(name=name.strip(), description=f"Departamento {name.strip()}")
        db.add(dept)
        db.commit()
        db.refresh(dept)
    return dept


def user_to_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        nombre=user.first_name,
        apellido=user.last_name or "-",
        usuario=user.username,
        depto=user.department.name if user.department else "-",
        rol=user.role,
    )


def format_operativo(value: Any) -> str:
    if value is None:
        return "No"
    text = str(value).strip().lower()
    return "Sí" if text in {"sí", "si", "true", "1", "yes"} else "No"


def computer_to_dict(record: ComputerRecord) -> Dict[str, Any]:
    return {
        "id": record.id,
        "serial": record.serial_number or "-",
        "usuario": record.owner_identifier or "-",
        "marca": record.brand or "-",
        "tipo": record.device_type or "PC",
        "depto": record.department.name if record.department else "-",
        "ip": record.ip_address or "-",
        "operativo": format_operativo(record.is_operational),
        "puerto": record.ethernet_port or "-",
        "nota": record.notes or "-",
    }


def printer_to_dict(record: PrinterRecord) -> Dict[str, Any]:
    return {
        "id": record.id,
        "serial": record.serial_number or "-",
        "usuario": record.model_name or "",
        "marca": record.brand or "-",
        "tipo": "Impresora",
        "depto": record.department.name if record.department else "-",
        "ip": record.ip_address or "-",
        "operativo": format_operativo(record.is_operational),
        "puerto": record.ethernet_port or "-",
        "nota": record.notes or "-",
    }


@app.on_event("startup")
def startup_event() -> None:
    try:
        with engine.begin() as conn:
            conn.execute(text("SELECT 1"))
        Base.metadata.create_all(bind=engine)
        seed_default_admin()
    except OperationalError:
        print("Database not available yet. Start PostgreSQL and rerun the app.")


def seed_default_admin() -> None:
    db = SessionLocal()
    try:
        super_admin = db.query(User).filter(User.username == SUPER_ADMIN_USERNAME).first()
        legacy_admin = db.query(User).filter(User.username == "admin").first()

        if legacy_admin and not super_admin:
            legacy_admin.username = SUPER_ADMIN_USERNAME
            legacy_admin.email = SUPER_ADMIN_USERNAME
            legacy_admin.role = "admin"
            legacy_admin.password_hash = hash_password(SUPER_ADMIN_USERNAME)
            db.commit()
            return

        if super_admin:
            try:
                verify_password(SUPER_ADMIN_USERNAME, super_admin.password_hash)
            except Exception:
                super_admin.password_hash = hash_password(SUPER_ADMIN_USERNAME)
                db.commit()
            return

        admin_dept = ensure_department(db, "Sistemas")
        user = User(
            first_name="Administrador",
            last_name="Sistema",
            username=SUPER_ADMIN_USERNAME,
            email=SUPER_ADMIN_USERNAME,
            password_hash=hash_password(SUPER_ADMIN_USERNAME),
            role="admin",
            department_id=admin_dept.id if admin_dept else None,
        )
        db.add(user)
        db.commit()
    finally:
        db.close()


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "app": APP_TITLE}


@app.get("/api/usuarios")
def list_users(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    users = db.query(User).order_by(User.id).all()
    output = []
    for user in users:
        output.append(
            {
                "id": user.id,
                "nombre": user.first_name,
                "apellido": user.last_name or "-",
                "usuario": user.username,
                "depto": user.department.name if user.department else "-",
                "rol": user.role,
            }
        )
    return output


@app.post("/api/usuarios", status_code=status.HTTP_201_CREATED)
def create_user(payload: UserPayload, db: Session = Depends(get_db)) -> Dict[str, Any]:
    require_super_admin(payload.requester, db)

    username = payload.usuario.strip()
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Usuario ya existe.")

    dept = ensure_department(db, payload.depto)
    usuario = User(
        first_name=payload.nombre.strip() or "Sin Nombre",
        last_name=payload.apellido.strip() or "-",
        username=username,
        email=username,
        password_hash=hash_password(payload.pass_ or "1234"),
        role=(payload.rol or "lectura").strip(),
        department_id=dept.id if dept else None,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return user_to_out(usuario).dict()


@app.put("/api/usuarios/{user_id}")
def update_user(user_id: int, payload: UserUpdatePayload, db: Session = Depends(get_db)) -> Dict[str, Any]:
    require_super_admin(payload.requester, db)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    if payload.nombre is not None:
        user.first_name = payload.nombre.strip() or "Sin Nombre"
    if payload.apellido is not None:
        user.last_name = payload.apellido.strip() or "-"
    if payload.usuario is not None:
        new_user = payload.usuario.strip()
        if new_user and db.query(User).filter(User.username == new_user, User.id != user_id).first():
            raise HTTPException(status_code=400, detail="El nombre de usuario ya existe.")
        user.username = new_user
        user.email = new_user
    if payload.depto is not None:
        dept = ensure_department(db, payload.depto)
        user.department_id = dept.id if dept else None
    if payload.rol is not None:
        user.role = payload.rol.strip() or "lectura"

    db.commit()
    db.refresh(user)
    return user_to_out(user).dict()


@app.delete("/api/usuarios/{user_id}")
def delete_user(
    user_id: int,
    requester: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    require_super_admin(requester, db)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    if user.username == SUPER_ADMIN_USERNAME:
        raise HTTPException(status_code=400, detail="No se puede eliminar el usuario administrador principal.")

    db.delete(user)
    db.commit()
    return {"message": "Usuario eliminado", "usuario": user.username}


@app.post("/api/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.query(User).filter(User.username == payload.username.strip()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")

    user_data = user_to_out(user)
    return AuthResponse(message="Login exitoso", user=user_data)


@app.post("/api/usuarios/{user_id}/reset-password")
def reset_password(user_id: int, payload: Dict[str, str], db: Session = Depends(get_db)) -> Dict[str, str]:
    requester_username = (payload.get("requester") or payload.get("solicitante") or "").strip()
    require_super_admin(requester_username, db)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    new_password = (payload.get("password") or payload.get("pass") or "1234").strip()
    user.password_hash = hash_password(new_password)
    db.commit()
    return {"message": "Contraseña actualizada", "usuario": user.username}


@app.get("/api/registros")
def list_records(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    computers = db.query(ComputerRecord).order_by(ComputerRecord.id).all()
    printers = db.query(PrinterRecord).order_by(PrinterRecord.id).all()
    combined = [computer_to_dict(item) for item in computers] + [printer_to_dict(item) for item in printers]
    return combined


@app.post("/api/registros", status_code=status.HTTP_201_CREATED)
def create_record(payload: GenericRecordPayload, db: Session = Depends(get_db)) -> Dict[str, Any]:
    if payload.tipo == "Impresora":
        return create_printer_record(payload, db)
    return create_computer_record(payload, db)


@app.put("/api/registros/{record_id}")
def update_record(record_id: int, payload: GenericRecordPayload, db: Session = Depends(get_db)) -> Dict[str, Any]:
    if payload.tipo == "Impresora":
        record = db.query(PrinterRecord).filter(PrinterRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Registro de impresora no encontrado.")

        dept = ensure_department(db, payload.depto)
        record.model_name = payload.usuario.strip()
        record.brand = payload.marca.strip() or "-"
        record.serial_number = payload.serial.strip() or "-"
        record.department_id = dept.id if dept else None
        record.ip_address = payload.ip.strip() or "-"
        record.is_operational = str(payload.operativo).strip().lower() in {"sí", "si", "true", "yes", "1"}
        record.ethernet_port = payload.puerto.strip() or "-"
        record.notes = payload.nota.strip() or "-"
        db.commit()
        db.refresh(record)
        return printer_to_dict(record)

    record = db.query(ComputerRecord).filter(ComputerRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Registro de equipo no encontrado.")

    dept = ensure_department(db, payload.depto)
    record.serial_number = payload.serial.strip() or "-"
    record.owner_identifier = payload.usuario.strip() or "-"
    record.brand = payload.marca.strip() or "-"
    record.device_type = (payload.tipo or "PC").upper()
    record.department_id = dept.id if dept else None
    record.ip_address = payload.ip.strip() or "-"
    record.is_operational = str(payload.operativo).strip().lower() in {"sí", "si", "true", "yes", "1"}
    record.ethernet_port = payload.puerto.strip() or "-"
    record.notes = payload.nota.strip() or "-"
    db.commit()
    db.refresh(record)
    return computer_to_dict(record)


@app.delete("/api/registros/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    record = db.query(ComputerRecord).filter(ComputerRecord.id == record_id).first()
    if record:
        db.delete(record)
        db.commit()
        return {"message": "Registro de equipo eliminado"}

    record = db.query(PrinterRecord).filter(PrinterRecord.id == record_id).first()
    if record:
        db.delete(record)
        db.commit()
        return {"message": "Registro de impresora eliminado"}

    raise HTTPException(status_code=404, detail="Registro no encontrado.")


def create_computer_record(payload: GenericRecordPayload, db: Session = Depends(get_db)) -> Dict[str, Any]:
    dept = ensure_department(db, payload.depto)
    record = ComputerRecord(
        serial_number=(payload.serial or "-").strip() or "-",
        owner_identifier=(payload.usuario or "-").strip() or "-",
        brand=(payload.marca or "-").strip() or "-",
        device_type=(payload.tipo or "PC").upper(),
        department_id=dept.id if dept else None,
        ip_address=(payload.ip or "-").strip() or "-",
        is_operational=str(payload.operativo).strip().lower() in {"sí", "si", "true", "yes", "1"},
        ethernet_port=(payload.puerto or "-").strip() or "-",
        notes=(payload.nota or "-").strip() or "-",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return computer_to_dict(record)


def create_printer_record(payload: GenericRecordPayload, db: Session = Depends(get_db)) -> Dict[str, Any]:
    dept = ensure_department(db, payload.depto)
    record = PrinterRecord(
        model_name=(payload.usuario or "").strip(),
        brand=(payload.marca or "-").strip() or "-",
        serial_number=(payload.serial or "-").strip() or "-",
        department_id=dept.id if dept else None,
        ip_address=(payload.ip or "-").strip() or "-",
        is_operational=str(payload.operativo).strip().lower() in {"sí", "si", "true", "yes", "1"},
        ethernet_port=(payload.puerto or "-").strip() or "-",
        notes=(payload.nota or "-").strip() or "-",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return printer_to_dict(record)


@app.get("/api/impresoras")
def list_printers(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    records = db.query(PrinterRecord).order_by(PrinterRecord.id).all()
    return [printer_to_dict(item) for item in records]


@app.get("/api/equipos")
def list_computers(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    records = db.query(ComputerRecord).order_by(ComputerRecord.id).all()
    return [computer_to_dict(item) for item in records]
