from services.user.get import UserGetMixin
from services.user.create import UserCreateMixin
from services.user.auth import AuthMixin


class UserServices(UserGetMixin, UserCreateMixin, AuthMixin):
    pass
    