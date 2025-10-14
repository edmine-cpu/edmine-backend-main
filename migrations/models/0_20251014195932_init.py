from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "category" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(32) NOT NULL UNIQUE,
    "name_uk" VARCHAR(64) NOT NULL,
    "name_en" VARCHAR(64) NOT NULL,
    "name_pl" VARCHAR(64) NOT NULL,
    "name_fr" VARCHAR(64),
    "name_de" VARCHAR(64),
    "slug_uk" VARCHAR(128),
    "slug_en" VARCHAR(128),
    "slug_pl" VARCHAR(128),
    "slug_fr" VARCHAR(128),
    "slug_de" VARCHAR(128),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "countries" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name_uk" VARCHAR(64) NOT NULL,
    "name_en" VARCHAR(64) NOT NULL,
    "name_pl" VARCHAR(64) NOT NULL,
    "name_fr" VARCHAR(64) NOT NULL,
    "name_de" VARCHAR(64) NOT NULL,
    "slug_uk" VARCHAR(128),
    "slug_en" VARCHAR(128),
    "slug_pl" VARCHAR(128),
    "slug_fr" VARCHAR(128),
    "slug_de" VARCHAR(128),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "cities" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name_uk" VARCHAR(64) NOT NULL,
    "name_en" VARCHAR(64) NOT NULL,
    "name_pl" VARCHAR(64) NOT NULL,
    "name_fr" VARCHAR(64) NOT NULL,
    "name_de" VARCHAR(64) NOT NULL,
    "slug_uk" VARCHAR(128),
    "slug_en" VARCHAR(128),
    "slug_pl" VARCHAR(128),
    "slug_fr" VARCHAR(128),
    "slug_de" VARCHAR(128),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "country_id" INT NOT NULL REFERENCES "countries" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "undercategory" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name_uk" VARCHAR(64),
    "name_en" VARCHAR(64),
    "name_pl" VARCHAR(64),
    "name_fr" VARCHAR(64),
    "name_de" VARCHAR(64),
    "slug_uk" VARCHAR(128),
    "slug_en" VARCHAR(128),
    "slug_pl" VARCHAR(128),
    "slug_fr" VARCHAR(128),
    "slug_de" VARCHAR(128),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "full_category_id" INT NOT NULL REFERENCES "category" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(64) NOT NULL,
    "email" VARCHAR(64) NOT NULL UNIQUE,
    "city" VARCHAR(64) NOT NULL,
    "password" VARCHAR(128) NOT NULL,
    "role" INT NOT NULL DEFAULT 0,
    "language" VARCHAR(2) NOT NULL DEFAULT 'en',
    "nickname" VARCHAR(64),
    "avatar" VARCHAR(500),
    "user_role" VARCHAR(20) NOT NULL DEFAULT 'customer',
    "profile_description" TEXT,
    "slug_uk" VARCHAR(128),
    "slug_en" VARCHAR(128),
    "slug_pl" VARCHAR(128),
    "slug_fr" VARCHAR(128),
    "slug_de" VARCHAR(128),
    "company_name_uk" VARCHAR(128),
    "company_name_en" VARCHAR(128),
    "company_name_pl" VARCHAR(128),
    "company_name_fr" VARCHAR(128),
    "company_name_de" VARCHAR(128),
    "company_description_uk" TEXT,
    "company_description_en" TEXT,
    "company_description_pl" TEXT,
    "company_description_fr" TEXT,
    "company_description_de" TEXT,
    "auto_translated_fields" JSONB,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "country_id" INT REFERENCES "countries" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "banned_ips" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "ip" VARCHAR(64) NOT NULL UNIQUE,
    "reason" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "banned_by_id" INT REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "bids" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title_uk" VARCHAR(128),
    "title_en" VARCHAR(128),
    "title_pl" VARCHAR(128),
    "title_fr" VARCHAR(128),
    "title_de" VARCHAR(128),
    "slug_uk" VARCHAR(256),
    "slug_en" VARCHAR(256),
    "slug_pl" VARCHAR(256),
    "slug_fr" VARCHAR(256),
    "slug_de" VARCHAR(256),
    "categories" JSONB,
    "under_categories" JSONB,
    "description_uk" TEXT,
    "description_en" TEXT,
    "description_pl" TEXT,
    "description_fr" TEXT,
    "description_de" TEXT,
    "budget" VARCHAR(32),
    "budget_type" VARCHAR(8),
    "files" JSONB,
    "auto_translated_fields" JSONB,
    "delete_token" VARCHAR(64) NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "author_id" INT REFERENCES "users" ("id") ON DELETE CASCADE,
    "city_id" INT REFERENCES "cities" ("id") ON DELETE CASCADE,
    "country_id" INT REFERENCES "countries" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "blog_articles" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title_uk" VARCHAR(256) NOT NULL,
    "title_en" VARCHAR(256),
    "title_pl" VARCHAR(256),
    "title_fr" VARCHAR(256),
    "title_de" VARCHAR(256),
    "slug_uk" VARCHAR(300),
    "slug_en" VARCHAR(300),
    "slug_pl" VARCHAR(300),
    "slug_fr" VARCHAR(300),
    "slug_de" VARCHAR(300),
    "content_uk" TEXT NOT NULL,
    "content_en" TEXT,
    "content_pl" TEXT,
    "content_fr" TEXT,
    "content_de" TEXT,
    "description_uk" VARCHAR(300),
    "description_en" VARCHAR(300),
    "description_pl" VARCHAR(300),
    "description_fr" VARCHAR(300),
    "description_de" VARCHAR(300),
    "keywords_uk" VARCHAR(500),
    "keywords_en" VARCHAR(500),
    "keywords_pl" VARCHAR(500),
    "keywords_fr" VARCHAR(500),
    "keywords_de" VARCHAR(500),
    "is_published" BOOL NOT NULL DEFAULT False,
    "auto_translated_fields" JSONB,
    "featured_image" VARCHAR(500),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "author_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "chats" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user1_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "user2_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "company" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(64) NOT NULL,
    "name_uk" VARCHAR(64),
    "name_en" VARCHAR(64),
    "name_pl" VARCHAR(64),
    "name_fr" VARCHAR(64),
    "name_de" VARCHAR(64),
    "description_uk" TEXT,
    "description_en" TEXT,
    "description_pl" TEXT,
    "description_fr" TEXT,
    "description_de" TEXT,
    "slug_name" VARCHAR(64),
    "slug_uk" VARCHAR(128),
    "slug_en" VARCHAR(128),
    "slug_pl" VARCHAR(128),
    "slug_fr" VARCHAR(128),
    "slug_de" VARCHAR(128),
    "city" TEXT,
    "country" TEXT,
    "auto_translated_fields" JSONB,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "owner_id" INT REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "messages" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "content" TEXT,
    "file_path" VARCHAR(512),
    "file_name" VARCHAR(256),
    "file_size" INT,
    "is_read" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "chat_id" INT NOT NULL REFERENCES "chats" ("id") ON DELETE CASCADE,
    "sender_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "password_reset_tokens" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "token" VARCHAR(255) NOT NULL UNIQUE,
    "code" VARCHAR(6) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expires_at" TIMESTAMPTZ NOT NULL,
    "is_used" BOOL NOT NULL DEFAULT False,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "users_category" (
    "users_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "category_id" INT NOT NULL REFERENCES "category" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_users_categ_users_i_ebdfd7" ON "users_category" ("users_id", "category_id");
CREATE TABLE IF NOT EXISTS "users_undercategory" (
    "users_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "undercategory_id" INT NOT NULL REFERENCES "undercategory" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_users_under_users_i_919e37" ON "users_undercategory" ("users_id", "undercategory_id");
CREATE TABLE IF NOT EXISTS "company_category" (
    "company_id" INT NOT NULL REFERENCES "company" ("id") ON DELETE CASCADE,
    "category_id" INT NOT NULL REFERENCES "category" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_company_cat_company_e47703" ON "company_category" ("company_id", "category_id");
CREATE TABLE IF NOT EXISTS "company_undercategory" (
    "company_id" INT NOT NULL REFERENCES "company" ("id") ON DELETE CASCADE,
    "undercategory_id" INT NOT NULL REFERENCES "undercategory" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_company_und_company_b5d708" ON "company_undercategory" ("company_id", "undercategory_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
