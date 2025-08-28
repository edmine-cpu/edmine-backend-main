from models import User


class UserCreateMixin():
    @staticmethod
    async def create_user(**kwargs):
        return await User.create(**kwargs)