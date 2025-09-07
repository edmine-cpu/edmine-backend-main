from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "company" ADD "slug_pl" VARCHAR(128);
        ALTER TABLE "company" ADD "name_en" VARCHAR(64);
        ALTER TABLE "company" ADD "name_fr" VARCHAR(64);
        ALTER TABLE "company" ADD "name_uk" VARCHAR(64);
        ALTER TABLE "company" ADD "slug_en" VARCHAR(128);
        ALTER TABLE "company" ADD "slug_fr" VARCHAR(128);
        ALTER TABLE "company" ADD "name_de" VARCHAR(64);
        ALTER TABLE "company" ADD "auto_translated_fields" JSONB;
        ALTER TABLE "company" ADD "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "company" ADD "slug_de" VARCHAR(128);
        ALTER TABLE "company" ADD "name_pl" VARCHAR(64);
        ALTER TABLE "company" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "company" ADD "slug_uk" VARCHAR(128);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "company" DROP COLUMN "slug_pl";
        ALTER TABLE "company" DROP COLUMN "name_en";
        ALTER TABLE "company" DROP COLUMN "name_fr";
        ALTER TABLE "company" DROP COLUMN "name_uk";
        ALTER TABLE "company" DROP COLUMN "slug_en";
        ALTER TABLE "company" DROP COLUMN "slug_fr";
        ALTER TABLE "company" DROP COLUMN "name_de";
        ALTER TABLE "company" DROP COLUMN "auto_translated_fields";
        ALTER TABLE "company" DROP COLUMN "updated_at";
        ALTER TABLE "company" DROP COLUMN "slug_de";
        ALTER TABLE "company" DROP COLUMN "name_pl";
        ALTER TABLE "company" DROP COLUMN "created_at";
        ALTER TABLE "company" DROP COLUMN "slug_uk";"""
