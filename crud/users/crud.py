from crud.users.get import UserGetMixin
from crud.users.create import UserCreateMixin 



class UserCRUD(UserGetMixin, UserCreateMixin):
    pass