from tortoise.models import Model
from tortoise import fields
from datetime import datetime, timedelta, timezone
import secrets
import random

class PasswordResetToken(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='reset_tokens')
    token = fields.CharField(max_length=255, unique=True)
    code = fields.CharField(max_length=6)  # 6-digit verification code
    created_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField()
    is_used = fields.BooleanField(default=False)
    
    class Meta:
        table = "password_reset_tokens"
    
    @classmethod
    async def create_for_user(cls, user):
        """Create new reset token for user"""
        # Delete old tokens
        await cls.filter(user=user).delete()
        
        # Generate new token and 6-digit code
        token = secrets.token_urlsafe(32)
        code = f"{random.randint(100000, 999999)}"  # 6-digit code
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)  # 15 minutes expiry
        
        reset_token = await cls.create(
            user=user,
            token=token,
            code=code,
            expires_at=expires_at
        )
        
        return reset_token
    
    async def is_valid(self):
        """Check if token is still valid"""
        return (
            not self.is_used and 
            datetime.now(timezone.utc) < self.expires_at
        )
    
    async def use_token(self):
        """Mark token as used"""
        self.is_used = True
        await self.save()
