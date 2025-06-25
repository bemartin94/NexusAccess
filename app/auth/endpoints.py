# app/auth/endpoints.py
from datetime import timedelta
from typing import Annotated, List # <<< CAMBIO IMPORTANTE: Agregado Annotated y List >>>

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select 
from sqlalchemy.orm import selectinload 

from core.database import AsyncSessionLocal
from core.models import User, Role # <<< CAMBIO IMPORTANTE: Asegúrate de importar Role >>>
from app.auth import schemas, security
from app.auth.security import get_db, get_current_active_user # <<< CAMBIO IMPORTANTE: Asegúrate de importar get_current_user >>>

router = APIRouter(tags=["Auth"]) # <<< CAMBIO IMPORTANTE: Cambiado el tag a "Auth" para coherencia >>>

# Dependencia para obtener la sesión de la base de datos (ya estaba, pero confirmamos)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Endpoint para obtener el token de acceso (login)
@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], # <<< CAMBIO IMPORTANTE: Agregado Annotated >>>
    db: AsyncSession = Depends(get_db)
):
    # Cargamos el usuario incluyendo sus roles y sede para el token
    # <<< CAMBIO IMPORTANTE: selectinload para cargar roles y venue >>>
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
    
    # Obtener los nombres de los roles del usuario
    user_role_names = user.role_names # <<< CAMBIO IMPORTANTE: Obtiene nombres de roles >>>
    
    # Obtener el ID de la sede del usuario (si existe)
    user_venue_id = user.venue_id # <<< CAMBIO IMPORTANTE: Obtiene ID de la sede >>>

    access_token = security.create_access_token(
        data={
            "sub": user.email, # 'sub' es el estándar para el sujeto del token
            "user_id": user.id, # <<< CAMBIO IMPORTANTE: Agregado user_id >>>
            "user_email": user.email, # <<< CAMBIO IMPORTANTE: Agregado user_email >>>
            "user_roles": user_role_names, # <<< CAMBIO IMPORTANTE: Agregado user_roles al payload del token >>>
            "venue_id": user_venue_id # <<< CAMBIO IMPORTANTE: Agregado venue_id al payload del token >>>
        },
        expires_delta=access_token_expires
    )
    # <<< CAMBIO IMPORTANTE: La respuesta del token ahora incluye user_id, user_email, user_roles y venue_id >>>
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        user_email=user.email,
        user_roles=user_role_names,
        venue_id=user_venue_id
    )

# Endpoint para crear un nuevo usuario
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
    # <<< CAMBIO IMPORTANTE: Requiere System Administrator para crear usuarios >>>
    current_user: User = Depends(security.has_role(security.SYSTEM_ADMINISTRATOR)) 
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

    # <<< CAMBIO IMPORTANTE: Asignar roles al nuevo usuario si se proporcionaron role_ids >>>
    if user_create.role_ids:
        # Obtener los objetos Role correspondientes a los IDs
        roles_result = await db.execute(select(Role).filter(Role.id.in_(user_create.role_ids)))
        roles = roles_result.scalars().all()
        
        if not roles:
            raise HTTPException(status_code=400, detail="One or more specified role IDs are invalid.")
            
        for role in roles:
            new_user.roles.append(role) # Asignar los roles al usuario
        
        await db.commit()
        await db.refresh(new_user) # Refrescar para cargar los roles asignados

    # Devolver UserResponse con los nombres de los roles
    # <<< CAMBIO IMPORTANTE: Incluye roles en la respuesta del nuevo usuario >>>
    return schemas.UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        last_name=new_user.last_name,
        phone=new_user.phone,
        venue_id=new_user.venue_id,
        roles=new_user.role_names # Usamos la propiedad role_names del modelo User
    )

# Endpoint de ejemplo para probar la autenticación y roles
# <<< CAMBIO IMPORTANTE: Nuevo endpoint para obtener información del usuario actual >>>
@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: Annotated[User, Depends(security.get_current_active_user)]):
    """
    Obtiene la información del usuario actual autenticado.
    Requiere que el usuario esté autenticado con un token válido.
    """
    return schemas.UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        venue_id=current_user.venue_id,
        roles=current_user.role_names # Incluimos los roles del usuario
    )

# Endpoint de ejemplo que requiere el rol "System Administrator"
# <<< CAMBIO IMPORTANTE: Nuevo endpoint con autorización por rol >>>
@router.get("/admin-only", response_model=dict)
async def admin_only_endpoint(
    current_user: Annotated[User, Depends(security.has_role(security.SYSTEM_ADMINISTRATOR))]
):
    """
    Endpoint de ejemplo que solo puede ser accedido por un System Administrator.
    """
    return {"message": f"Bienvenido, Administrador de Sistema {current_user.email}!"}

# Endpoint de ejemplo que requiere el rol "Venue Supervisor"
# <<< CAMBIO IMPORTANTE: Nuevo endpoint con autorización por rol >>>
@router.get("/supervisor-only", response_model=dict)
async def supervisor_only_endpoint(
    current_user: Annotated[User, Depends(security.has_role(security.VENUE_SUPERVISOR))]
):
    """
    Endpoint de ejemplo que solo puede ser accedido por un Venue Supervisor.
    """
    return {"message": f"Bienvenido, Supervisor de Sede {current_user.email} en la sede {current_user.venue.name if current_user.venue else 'N/A'}!"}

# Endpoint de ejemplo que requiere el rol "Guest User"
# <<< CAMBIO IMPORTANTE: Nuevo endpoint con autorización por rol >>>
@router.get("/guest-only", response_model=dict)
async def guest_only_endpoint(
    current_user: Annotated[User, Depends(security.has_role(security.GUEST_USER))]
):
    """
    Endpoint de ejemplo que solo puede ser accedido por un Guest User.
    """
    return {"message": f"Bienvenido, Usuario Invitado {current_user.email}!"}

# Endpoint para listar todos los usuarios (solo para System Administrator)
# <<< CAMBIO IMPORTANTE: Nuevo endpoint para listar usuarios, restringido por rol >>>
@router.get("/users", response_model=List[schemas.UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(security.has_role(security.SYSTEM_ADMINISTRATOR)) # Requiere admin
):
    # Cargamos todos los usuarios con sus roles
    result = await db.execute(select(User).options(selectinload(User.roles)))
    users = result.scalars().all()
    # Mapeamos los usuarios a nuestro esquema de respuesta
    return [
        schemas.UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            last_name=user.last_name,
            phone=user.phone,
            venue_id=user.venue_id,
            roles=user.role_names
        ) for user in users
    ]