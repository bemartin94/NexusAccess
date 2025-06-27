import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.hash import bcrypt # Asegúrate de que passlib esté instalado: pip install passlib
from core.database import AsyncSessionLocal, engine, Base
from core.models import Role, User

async def init_db():
    # Asegurarse de que las tablas existen. Esto debería ser manejado por Alembic.
    # No eliminamos ni recreamos las tablas aquí para preservar los datos.
    # Si las tablas no existen, Alembic debe haber sido ejecutado previamente.
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # ¡COMENTA O ELIMINA ESTA LÍNEA!
        # await conn.run_sync(Base.metadata.create_all) # ¡COMENTA O ELIMINA ESTA LÍNEA!
        print("Database tables are assumed to be managed by Alembic.")

    async with AsyncSessionLocal() as session:
        # 1. Create Roles if they don't exist
        roles_to_create = ["System Administrator", "Venue Supervisor", "Guest User"]
        
        # Obtener los roles existentes para evitar duplicados
        existing_roles_result = await session.execute(select(Role))
        existing_roles = {r.name: r for r in existing_roles_result.scalars()}

        for role_name in roles_to_create:
            if role_name not in existing_roles:
                new_role = Role(name=role_name)
                session.add(new_role)
                print(f"Adding role: {role_name}")
                existing_roles[role_name] = new_role # Add to dict to make it available immediately

        await session.commit() # Commit roles first to ensure they have IDs
        
        # Refresh the session or re-query to ensure all roles (including newly added) are tracked
        roles_in_db_result = await session.execute(select(Role))
        roles_in_db = {r.name: r for r in roles_in_db_result.scalars()}


        # 2. Create an initial System Administrator user if it doesn't exist
        admin_email = "admin@example.com"
        admin_password = "password" # ¡Cambia esto en un entorno real!
        
        existing_admin_result = await session.execute(select(User).filter(User.email == admin_email))
        existing_admin = existing_admin_result.scalars().first()

        if not existing_admin:
            admin_role = roles_in_db.get("System Administrator")
            if admin_role:
                hashed_password = bcrypt.hash(admin_password)
                new_admin_user = User(
                    email=admin_email,
                    password=hashed_password,
                    name="System",
                    last_name="Admin",
                    phone="111222333",
                    venue_id=None, # Admins might not be tied to a specific venue
                    role_id=admin_role.id # CAMBIO CLAVE AQUÍ: Asigna el ID del rol directamente
                )
                session.add(new_admin_user)
                
                print(f"Creating initial System Administrator: {admin_email}")
                
                await session.commit() # Commit para guardar el usuario con su rol
                # No es necesario flush() ni new_admin_user.roles.append()
                # porque el role_id ya fue asignado.
            else:
                print("System Administrator role not found, cannot create admin user.")
        else:
            print(f"System Administrator '{admin_email}' already exists. Skipping creation.")

    print("Database seeding complete.")

if __name__ == "__main__":
    asyncio.run(init_db())