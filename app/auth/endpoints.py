# app/auth/endpoints.py
from datetime import timedelta
from typing import Annotated, List 

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select 
from sqlalchemy.orm import selectinload 

from core.database import get_db # <<< CAMBIO AQUÍ: Importa get_db desde core.database >>>
from core.models import User, Role 
from app.auth import schemas, security # Importa el módulo de seguridad

router = APIRouter(tags=["Auth"])

# Eliminada la definición duplicada de get_db() aquí.

# Endpoint para obtener el token de acceso (login)
@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: AsyncSession = Depends(get_db)
):
    # Cargamos el usuario incluyendo sus roles y sede para el token
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles), selectinload(User.venue))
        .filter(User.email == form_data.username) # username es el email
    )
    user = result.scalars().first()

    if not user or not security.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Preparamos los datos para el token incluyendo roles y venue_id
    access_token_expires = timedelta(minutes=security.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Obtener los nombres de los roles del usuario (usa la propiedad role_names del modelo User)
    user_role_names = user.role_names 
    
    # Obtener el ID de la sede del usuario (si existe)
    user_venue_id = user.venue_id 

    # Crear el token de acceso usando el ID, email, roles y venue_id
    access_token = security.create_access_token(
        # security.create_access_token ahora espera un objeto User completo
        user=user, 
        expires_delta=access_token_expires
    )
    
    # La respuesta del token ahora incluye user_id, user_email, user_roles y venue_id
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        user_email=user.email,
        user_roles=user_role_names,
        venue_id=user_venue_id
    )

# Endpoint para crear un nuevo usuario (solo para System Administrator)
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: schemas.UserCreate,
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
        venue_id=user_create.venue_id
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Asignar roles al nuevo usuario si se proporcionaron role_ids
    if user_create.role_ids:
        roles_result = await db.execute(select(Role).filter(Role.id.in_(user_create.role_ids)))
        roles = roles_result.scalars().all()
        
        if not roles:
            raise HTTPException(status_code=400, detail="One or more specified role IDs are invalid.")
            
        for role in roles:
            new_user.roles.append(role) # Asignar los roles al usuario
        
        await db.commit()
        await db.refresh(new_user) # Refrescar para cargar los roles asignados

    # Devolver UserResponse con los nombres de los roles
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
    # Cargamos todos los usuarios con sus roles
    result = await db.execute(select(User).options(selectinload(User.roles)))
    users = result.scalars().all()
    # Mapeamos los usuarios a nuestro esquema de respuesta
    # Usamos model_validate para el mapeo automático de propiedades computadas como 'roles'
    return [schemas.UserResponse.model_validate(user) for user in users]
 