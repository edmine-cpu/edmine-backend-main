from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bids" ADD "main_language" VARCHAR(2) DEFAULT 'en';
        ALTER TABLE "bids" DROP COLUMN "main_lang";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bids" ADD "main_lang" VARCHAR(3);
        ALTER TABLE "bids" DROP COLUMN "main_language";"""
