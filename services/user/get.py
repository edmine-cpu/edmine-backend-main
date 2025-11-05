from crud.users.crud import UserCRUD
from fastapi import HTTPException

    

class UserGetMixin():
    @staticmethod
    async def get_users(search: str = None):
        users = await UserCRUD.get_users(search=search)
        if not users:
            raise HTTPException(status_code=404, detail="No users found")
        return users    
    
    
    @staticmethod
    async def get_user_by_id(user_id: int):
        user = await UserCRUD.get_user_by_id(id=user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user





