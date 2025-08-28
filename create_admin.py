import asyncio
from tortoise import Tortoise
from models.user import User
from routers.secur import get_password_hash

async def main():
    await Tortoise.init(
        db_url='postgres://postgres:WordPass_!forPostgres_%40@localhost:5432/makeasap',
        modules={'models': ['models.user', 'models.actions', 'models.categories', 'models.places', 'models.chat']}
    )
    await Tortoise.generate_schemas()
    
    # Check if admin already exists
    admin = await User.get_or_none(email='admin@gmail.com')
    if admin:
        print(f'Admin user already exists: {admin.email}')
        # Update role to admin
        admin.role = 1
        admin.user_role = 'admin'
        await admin.save()
        print(f'Updated admin role for: {admin.email}')
    else:
        # Create new admin user
        hashed_password = get_password_hash('password123')
        admin = await User.create(
            name='Admin',
            email='admin@gmail.com',
            password=hashed_password,
            city='Admin City',
            role=1,
            user_role='admin'
        )
        print(f'Created admin user: {admin.email}')
    
    # Also update admin1@gmail.com if exists
    admin1 = await User.get_or_none(email='admin1@gmail.com')
    if admin1:
        admin1.role = 1
        admin1.user_role = 'admin'
        await admin1.save()
        print(f'Updated admin role for: {admin1.email}')
    
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())
