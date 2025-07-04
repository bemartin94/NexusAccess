import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.hash import bcrypt
from core.database import AsyncSessionLocal, engine, Base 
from core.models import Role, User, IdCardType

async def init_db():
    print("Database tables are assumed to be managed by Alembic.")

    async with AsyncSessionLocal() as session:
        roles_to_create = ["System Administrator", "Venue Supervisor", "Receptionist"]
        
        try:
            existing_roles_result = await session.execute(select(Role))
            existing_roles = {r.name: r for r in existing_roles_result.scalars()}
        except Exception as e:
            print(f"Error al consultar la tabla 'roles'. Asegúrate de que la migración ha sido aplicada: {e}")
            raise


        for role_name in roles_to_create:
            if role_name not in existing_roles:
                new_role = Role(name=role_name)
                session.add(new_role)
                print(f"Agregando rol: {role_name}")
                existing_roles[role_name] = new_role

        await session.commit()
        
        roles_in_db_result = await session.execute(select(Role))
        roles_in_db = {r.name: r for r in roles_in_db_result.scalars()}


        # 2. Crear tipos de documento de identidad (IdCardType) si no existen
        id_card_types_to_create = ["DNI", "Pasaporte", "Cédula de Extranjería", "Licencia de Conducir"]

        try:
            existing_id_card_types_result = await session.execute(select(IdCardType))
            existing_id_card_types = {t.name: t for t in existing_id_card_types_result.scalars()}
        except Exception as e:
            print(f"Error al consultar la tabla 'id_card_types'. Asegúrate de que la migración ha sido aplicada: {e}")
            raise

        for id_card_type_name in id_card_types_to_create:
            if id_card_type_name not in existing_id_card_types:
                new_id_card_type = IdCardType(name=id_card_type_name)
                session.add(new_id_card_type)
                print(f"Agregando tipo de documento de identidad: {id_card_type_name}")
        
        await session.commit()

        # 3. Crear un usuario System Administrator inicial si no existe
        admin_email = "admin@example.com"
        admin_password = "password" 
        
        try:
            existing_admin_result = await session.execute(select(User).filter(User.email == admin_email))
            existing_admin = existing_admin_result.scalars().first()
        except Exception as e:
            print(f"Error al consultar la tabla 'users'. Asegúrate de que la migración ha sido aplicada: {e}")
            raise


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
                    venue_id=None,
                    role_id=admin_role.id
                )
                session.add(new_admin_user)
                
                print(f"Creando usuario System Administrator inicial: {admin_email}")
                
                await session.commit()
            else:
                print("Rol 'System Administrator' no encontrado, no se puede crear el usuario admin.")
        else:
            print(f"Usuario System Administrator '{admin_email}' ya existe. Saltando creación.")

    print("Siembra de base de datos completa.")
    await engine.dispose() 

if __name__ == "__main__":
    asyncio.run(init_db())