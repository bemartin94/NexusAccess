from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # Importa para el esquema de login compatible con OAuth2
from sqlalchemy.ext.asyncio import AsyncSession

from app.users import dal as users_dal # Importa el DAL de usuarios
from app.users import schemas as users_schemas # Importa los schemas de usuarios (ej. UserCreate)
from app.auth import schemas as auth_schemas # Importa los schemas de autenticación (UserLogin, Token)
from app.auth import security as auth_security # Importa el módulo de seguridad (hashing, JWT)
from core.database import AsyncSessionLocal # Importa la función para obtener la sesión de DB
from core.models import User # Asegúrate de que User esté importado si se usa directamente (aunque aquí no se usa en el endpoint)

router = APIRouter(tags=["Authentication"])

# Dependencia para obtener la sesión de la base de datos
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Endpoint de Registro de Usuarios
@router.post("/register", response_model=users_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: users_schemas.UserCreate, # Recibe la contraseña en texto plano aquí desde el frontend
    db: AsyncSession = Depends(get_db)
):
    # 1. Verificar si ya existe un usuario con el mismo email
    existing_user = await users_dal.UserDAL(db).get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists."
        )
    
    # 2. Hashear la contraseña antes de guardarla
    # user_in es el objeto Pydantic UserCreate que FastAPI ha creado a partir de la solicitud.
    # user_in.password contiene la contraseña en texto plano.
    hashed_password = auth_security.get_password_hash(user_in.password)

    # 3. Crear una NUEVA instancia del modelo UserCreate
    # Esta nueva instancia tendrá la contraseña hasheada, lista para ser persistida.
    # Usamos .model_copy() para crear una copia de user_in y sobrescribir solo el campo 'password'.
    user_to_create = user_in.model_copy(update={"password": hashed_password})

    # 4. Crear el usuario en la base de datos a través del DAL
    # user_to_create es el objeto UserCreate con la contraseña ya hasheada.
    new_user = await users_dal.UserDAL(db).create_user(user_to_create)
    
    return new_user

# Endpoint de Inicio de Sesión
# Usamos OAuth2PasswordRequestForm para que sea compatible con los estándares de OAuth2 y Swagger UI
@router.post("/token", response_model=auth_schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), # Espera username (email) y password
    db: AsyncSession = Depends(get_db)
):
    # Obtener el usuario por email (el username en OAuth2PasswordRequestForm es el email aquí)
    user = await users_dal.UserDAL(db).get_user_by_email(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar la contraseña hasheada
    # form_data.password es la contraseña en texto plano del formulario de login.
    # user.password debe ser la contraseña hasheada obtenida de la DB.
    if not auth_security.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear el token de acceso JWT
    access_token_expires = timedelta(minutes=auth_security.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_security.create_access_token(
        data={"sub": user.email}, # "sub" es el estándar para el sujeto (identificador del usuario)
        expires_delta=access_token_expires
    )
    
    # Retornar el token y la información del usuario/sede
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,         # Incluye el ID del usuario
        "venue_id": user.venue_id   # Incluye el ID de la sede del usuario
    }