-- Base de datos para el sistema de inventario de equipos y usuarios
-- Adaptada del HTML: login, usuarios, registros de PC/Laptop y registros de impresoras

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TYPE user_role AS ENUM ('admin', 'lectura');

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150),
    password_hash TEXT NOT NULL,
    role user_role NOT NULL DEFAULT 'lectura',
    department_id INTEGER REFERENCES departments(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TYPE device_type AS ENUM ('PC', 'LAPTOP');

CREATE TABLE IF NOT EXISTS computer_records (
    id SERIAL PRIMARY KEY,
    serial_number VARCHAR(100) NOT NULL,
    owner_identifier VARCHAR(100),
    owner_user_id INTEGER REFERENCES users(id),
    brand VARCHAR(120),
    device_type device_type NOT NULL DEFAULT 'PC',
    department_id INTEGER REFERENCES departments(id),
    ip_address VARCHAR(45),
    is_operational BOOLEAN NOT NULL DEFAULT TRUE,
    ethernet_port VARCHAR(120),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS printer_records (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(150),
    brand VARCHAR(120),
    serial_number VARCHAR(100),
    ip_address VARCHAR(45),
    ethernet_port VARCHAR(120),
    department_id INTEGER REFERENCES departments(id),
    is_operational BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_computer_serial
    ON computer_records ((NULLIF(serial_number, '-')));

CREATE UNIQUE INDEX IF NOT EXISTS uq_printer_serial
    ON printer_records ((NULLIF(serial_number, '-')));

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_computer_records_updated_at
BEFORE UPDATE ON computer_records
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_printer_records_updated_at
BEFORE UPDATE ON printer_records
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

INSERT INTO departments (name, description)
VALUES
    ('Sistemas', 'Área de soporte y administración del sistema'),
    ('Contabilidad', 'Departamento contable'),
    ('Administración', 'Área administrativa'),
    ('Recursos Humanos', 'Departamental de personal')
ON CONFLICT (name) DO NOTHING;

INSERT INTO users (first_name, last_name, username, email, password_hash, role, department_id)
VALUES (
    'Administrador',
    'Sistema',
    'admin',
    'admin',
    crypt('admin', gen_salt('bf')),
    'admin',
    (SELECT id FROM departments WHERE name = 'Sistemas')
)
ON CONFLICT (username) DO NOTHING;

-- Ejemplo de consulta útil:
-- SELECT * FROM computer_records WHERE is_operational = TRUE;
-- SELECT * FROM printer_records WHERE ip_address LIKE '192.168.1.%';
