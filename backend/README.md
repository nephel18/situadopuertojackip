# Backend FastAPI para Situado de Puerto Jack e IP

Este backend conecta el sistema web con PostgreSQL y expone endpoints REST para:

- Login de usuarios
- Mantenimiento de usuarios
- Registro de equipos PC/Laptop
- Registro de impresoras
- Consulta y exportación de inventario

## Requisitos

- Python 3.11+
- PostgreSQL 14+

## Instalación

1. Crear y activar un entorno virtual
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Copiar el ejemplo de variables de entorno:

```bash
copy .env.example .env
```

4. Crear la base de datos PostgreSQL:

```sql
CREATE DATABASE situado_db;
```

5. Ejecutar la API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Login por defecto

- Usuario: `bsalazar`
- Contraseña: `bsalazar`

## Seguridad y administración de usuarios

La administración de usuarios es **exclusiva del superadmin** (`bsalazar`):

- Solo `bsalazar` puede crear usuarios, editar datos, cambiar contraseñas y otorgar/revocar el privilegio de administrador.
- Todos los endpoints de gestión de usuarios validan en el backend que el solicitante sea `bsalazar` mediante el campo `requester` (cuerpo de la petición o query param `?requester=` en `DELETE`).
- No se puede eliminar la cuenta de `bsalazar` ni la propia cuenta activa.
- El hash de contraseña nunca se expone en las respuestas de la API.

El frontend aplica las mismas reglas de permisos (oculta los botones a usuarios sin privilegio), pero la autorización real la aplica el backend.

## Endpoints principales

- `GET /api/health`
- `POST /api/login`
- `GET /api/usuarios`
- `POST /api/usuarios` (requiere `requester` superadmin)
- `PUT /api/usuarios/{user_id}` (requiere `requester` superadmin)
- `DELETE /api/usuarios/{user_id}` (requiere query `?requester=` superadmin)
- `POST /api/usuarios/{user_id}/reset-password` (requiere `requester` superadmin)
- `GET /api/registros`
- `POST /api/registros`
- `PUT /api/registros/{record_id}`
- `DELETE /api/registros/{record_id}`
- `GET /api/equipos`
- `GET /api/impresoras`

## CORS

El backend está configurado para aceptar peticiones desde cualquier origen para facilitar la integración con el frontend actual.

## Despliegue en Render

Este proyecto incluye un archivo [render.yaml](../render.yaml) para desplegar el backend y la base de datos PostgreSQL en Render.

### Pasos

1. Crea una cuenta en Render.
2. Conecta este repositorio.
3. Render detectará el archivo `render.yaml`.
4. Confirma la creación del servicio web y la base de datos PostgreSQL.
5. Cuando el servicio termine de construirse, usa la URL pública del backend.

Ejemplo de URL esperada:

```text
https://situado-backend.onrender.com
```

6. En el frontend, actualiza la URL base de la API en JavaScript:

```js
const API_BASE = 'https://situado-backend.onrender.com';
```

### Variables de entorno importantes

- `DATABASE_URL`: se crea automáticamente desde la base de datos PostgreSQL de Render.
- `APP_TITLE`: nombre de tu aplicación.
- `APP_VERSION`: versión actual.
- `DEBUG`: debe estar en `false` en producción.

### Login inicial

- Usuario: `bsalazar`
- Contraseña: `bsalazar`
