from datetime import timedelta
from typing import Annotated, List, Optional # Importa Optional si no estaba ya

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select 
# from sqlalchemy.orm import selectinload # YA NO NECESITAMOS selectinload(User.roles)
from sqlalchemy.orm import selectinload 
from core.database import get_db
from core.models import User, Role # Asegúrate de que tus modelos ya estén actualizados con el campo role_id
from app.auth import schemas, security

router = APIRouter(tags=["Auth"])

# Endpoint para obtener el token de acceso (login)
@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: AsyncSession = Depends(get_db)
):
    # Cargamos el usuario incluyendo su rol y sede para el token
    # Ya no es necesario selectinload(User.roles) si la relación es uno a uno con Role
    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.venue)) # Cargamos el objeto Role único
        .filter(User.email == form_data.username) # username es el email
    )
    user = result.scalars().first()

    if not user or not security.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Preparamos los datos para el token incluyendo rol y venue_id
    access_token_expires = timedelta(minutes=security.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Obtener el nombre del rol del usuario (usa la nueva propiedad role_name del modelo User)
    user_role_name = user.role_name # Ahora es un solo nombre de rol
    
    # Obtener el ID de la sede del usuario (si existe)
    user_venue_id = user.venue_id 

    # Crear el token de acceso usando el ID, email, rol y venue_id
    access_token = security.create_access_token(
        user=user, 
        expires_delta=access_token_expires
    )
    
    # La respuesta del token ahora incluye user_id, user_email, user_role y venue_id
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        user_email=user.email,
        user_role=user_role_name, # Cambiado de user_roles a user_role
        venue_id=user_venue_id
    )

# Endpoint para crear un nuevo usuario (solo para System Administrator)
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: schemas.UserCreate, # Asegúrate de que este esquema ahora tenga role_id y no role_ids
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(security.has_role(security.SYSTEM_ADMINISTRATOR)) # Requiere System Administrator
):
    # Verificar si el usuario ya existe
    result = await db.execute(select(User).filter(User.email == user_create.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash de la contraseña
    hashed_password = security.get_password_hash(user_create.password)

    # Crear el nuevo usuario
    new_user = User(
        email=user_create.email,
        password=hashed_password,
        name=user_create.name,
        last_name=user_create.last_name,
        phone=user_create.phone,
        venue_id=user_create.venue_id,
        role_id=user_create.role_id # Asignar el role_id directamente
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user) # Refrescar para cargar el objeto Role relacionado si se necesita inmediatamente

    # Ya no se necesita asignar roles en un bucle, ya que se asignó directamente con role_id
    # Puedes cargar el objeto Role para el refresh si es necesario, pero SQLAlchemy lo hará lazy-load por defecto
    # si se accede a new_user.role

    # Devolver UserResponse con el nombre del rol
    return schemas.UserResponse.model_validate(new_user) # Usa model_validate para el objeto User


# Endpoint de ejemplo para obtener información del usuario actual
@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: Annotated[User, Depends(security.get_current_active_user)]):
    """
    Obtiene la información del usuario actual autenticado.
    Requiere que el usuario esté autenticado con un token válido.
    """
    return schemas.UserResponse.model_validate(current_user)


# Endpoint de ejemplo que requiere el rol "System Administrator"
@router.get("/admin-only", response_model=dict)
async def admin_only_endpoint(
    current_user: Annotated[User, Depends(security.has_role(security.SYSTEM_ADMINISTRATOR))]
):
    """
    Endpoint de ejemplo que solo puede ser accedido por un System Administrator.
    """
    return {"message": f"Bienvenido, Administrador de Sistema {current_user.email}!"}

# Endpoint de ejemplo que requiere el rol "Venue Supervisor"
@router.get("/supervisor-only", response_model=dict)
async def supervisor_only_endpoint(
    current_user: Annotated[User, Depends(security.has_role(security.VENUE_SUPERVISOR))]
):
    """
    Endpoint de ejemplo que solo puede ser accedido por un Venue Supervisor.
    """
    return {"message": f"Bienvenido, Supervisor de Sede {current_user.email} en la sede {current_user.venue.name if current_user.venue else 'N/A'}!"}

# Endpoint de ejemplo que requiere el rol "Guest User"
@router.get("/guest-only", response_model=dict)
async def guest_only_endpoint(
    current_user: Annotated[User, Depends(security.has_role(security.GUEST_USER))]
):
    """
    Endpoint de ejemplo que solo puede ser accedido por un Guest User.
    """
    return {"message": f"Bienvenido, Usuario Invitado {current_user.email}!"}

# Endpoint para listar todos los usuarios (solo para System Administrator)
@router.get("/users", response_model=List[schemas.UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(security.has_role(security.SYSTEM_ADMINISTRATOR)) # Requiere admin
):
    # Cargamos todos los usuarios con su rol
    result = await db.execute(select(User).options(selectinload(User.role))) # Cargamos el objeto Role único
    users = result.scalars().all()
    # Mapeamos los usuarios a nuestro esquema de respuesta
    return [schemas.UserResponse.model_validate(user) for user in users]