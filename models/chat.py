from tortoise import models, fields


class Chat(models.Model):
    id = fields.IntField(pk=True)
    user1 = fields.ForeignKeyField('models.User', related_name='chats_as_user1')
    user2 = fields.ForeignKeyField('models.User', related_name='chats_as_user2')
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'chats'


class Message(models.Model):
    id = fields.IntField(pk=True)
    chat = fields.ForeignKeyField('models.Chat', related_name='messages')
    sender = fields.ForeignKeyField('models.User', related_name='sent_messages')
    content = fields.TextField(null=True)
    file_path = fields.CharField(max_length=512, null=True)
    file_name = fields.CharField(max_length=256, null=True)
    file_size = fields.IntField(null=True)
    is_read = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'messages'


class BannedIP(models.Model):
    id = fields.IntField(pk=True)
    ip = fields.CharField(max_length=64, unique=True)
    reason = fields.TextField(null=True)
    banned_by = fields.ForeignKeyField('models.User', related_name='banned_ips', null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'banned_ips'


