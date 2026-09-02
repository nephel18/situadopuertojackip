import os
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "situado_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        cursor_factory=RealDictCursor,
    )
    conn.autocommit = True
    return conn


def create_database_if_not_exists(db_name: str = "situado_db"):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname="postgres",
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s;",
            (db_name,),
        )
        exists = cur.fetchone()
        if not exists:
            cur.execute(f'CREATE DATABASE "{db_name}";')
    conn.close()


def run_sql_file(sql_path: str):
    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.close()


def add_user(first_name: str, last_name: str, username: str, password: str, role: str = "lectura", department_name: Optional[str] = None):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (first_name, last_name, username, email, password_hash, role, department_id)
            VALUES (%s, %s, %s, %s, crypt(%s, gen_salt('bf')), %s,
                    (SELECT id FROM departments WHERE name = %s))
            ON CONFLICT (username) DO UPDATE
            SET first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                email = EXCLUDED.email,
                password_hash = EXCLUDED.password_hash,
                role = EXCLUDED.role,
                department_id = EXCLUDED.department_id
            RETURNING *;
            """,
            (first_name, last_name, username, username, password, role, department_name or "Sistemas"),
        )
        return cur.fetchone()
    

def add_computer_record(
    serial_number: str,
    owner_identifier: str,
    brand: str,
    device_type: str,
    department_name: Optional[str] = None,
    ip_address: Optional[str] = None,
    is_operational: bool = True,
    ethernet_port: Optional[str] = None,
    notes: Optional[str] = None,
):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO computer_records (
                serial_number, owner_identifier, brand, device_type, department_id,
                ip_address, is_operational, ethernet_port, notes
            )
            VALUES (
                %s, %s, %s, %s,
                (SELECT id FROM departments WHERE name = %s),
                %s, %s, %s, %s
            )
            RETURNING *;
            """,
            (
                serial_number,
                owner_identifier,
                brand,
                device_type,
                department_name or "Sistemas",
                ip_address,
                is_operational,
                ethernet_port,
                notes,
            ),
        )
        return cur.fetchone()


def add_printer_record(
    model_name: str,
    brand: str,
    serial_number: str,
    department_name: Optional[str] = None,
    ip_address: Optional[str] = None,
    is_operational: bool = True,
    ethernet_port: Optional[str] = None,
    notes: Optional[str] = None,
):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO printer_records (
                model_name, brand, serial_number, department_id,
                ip_address, is_operational, ethernet_port, notes
            )
            VALUES (
                %s, %s, %s,
                (SELECT id FROM departments WHERE name = %s),
                %s, %s, %s, %s
            )
            RETURNING *;
            """,
            (
                model_name,
                brand,
                serial_number,
                department_name or "Sistemas",
                ip_address,
                is_operational,
                ethernet_port,
                notes,
            ),
        )
        return cur.fetchone()


def login_user(username: str, password: str):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM users
            WHERE username = %s AND password_hash = crypt(%s, password_hash);
            """,
            (username, password),
        )
        return cur.fetchone()


if __name__ == "__main__":
    create_database_if_not_exists("situado_db")
    run_sql_file("database_schema.sql")

    add_user("Administrador", "Sistema", "admin", "admin", role="admin", department_name="Sistemas")
    add_computer_record(
        serial_number="SN-00123",
        owner_identifier="jperez",
        brand="Dell",
        device_type="PC",
        department_name="Contabilidad",
        ip_address="192.168.1.10",
        is_operational=True,
        ethernet_port="SW1-P24",
        notes="Equipo activo",
    )
    add_printer_record(
        model_name="HP LaserJet Pro",
        brand="HP",
        serial_number="SN-IMP-001",
        department_name="Administración",
        ip_address="192.168.1.20",
        is_operational=True,
        ethernet_port="SW1-P10",
        notes="Impresora principal",
    )

    print("Base de datos y datos de ejemplo creados correctamente.")
