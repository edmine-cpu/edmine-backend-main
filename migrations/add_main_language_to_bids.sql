-- Миграция: добавление поля main_language в таблицу bids
-- Дата: 2025-10-14
-- Описание: Добавляет поле main_language для хранения основного языка бида

-- Шаг 1: Добавить колонку main_language
ALTER TABLE bids
ADD COLUMN IF NOT EXISTS main_language VARCHAR(2) DEFAULT 'en';

-- Шаг 2: Создать индекс для ускорения поиска по языку
CREATE INDEX IF NOT EXISTS idx_bids_main_language ON bids(main_language);

-- Шаг 3: Обновить существующие записи (определить язык по заполненным полям)
-- Приоритет: uk > en > pl > fr > de
UPDATE bids
SET main_language = CASE
    WHEN title_uk IS NOT NULL AND title_uk != '' THEN 'uk'
    WHEN title_en IS NOT NULL AND title_en != '' THEN 'en'
    WHEN title_pl IS NOT NULL AND title_pl != '' THEN 'pl'
    WHEN title_fr IS NOT NULL AND title_fr != '' THEN 'fr'
    WHEN title_de IS NOT NULL AND title_de != '' THEN 'de'
    ELSE 'en'  -- Дефолт на английский
END
WHERE main_language IS NULL OR main_language = '';

-- Шаг 4: Добавить комментарий к колонке
COMMENT ON COLUMN bids.main_language IS 'Основной язык бида (uk, en, pl, fr, de). Определяется автоматически при создании.';

-- Шаг 5: Вывести статистику
DO $$
DECLARE
    total_count INT;
    uk_count INT;
    en_count INT;
    pl_count INT;
    fr_count INT;
    de_count INT;
BEGIN
    SELECT COUNT(*) INTO total_count FROM bids;
    SELECT COUNT(*) INTO uk_count FROM bids WHERE main_language = 'uk';
    SELECT COUNT(*) INTO en_count FROM bids WHERE main_language = 'en';
    SELECT COUNT(*) INTO pl_count FROM bids WHERE main_language = 'pl';
    SELECT COUNT(*) INTO fr_count FROM bids WHERE main_language = 'fr';
    SELECT COUNT(*) INTO de_count FROM bids WHERE main_language = 'de';

    RAISE NOTICE '=== Статистика миграции ===';
    RAISE NOTICE 'Всего бидов: %', total_count;
    RAISE NOTICE 'Украинский (uk): %', uk_count;
    RAISE NOTICE 'Английский (en): %', en_count;
    RAISE NOTICE 'Польский (pl): %', pl_count;
    RAISE NOTICE 'Французский (fr): %', fr_count;
    RAISE NOTICE 'Немецкий (de): %', de_count;
    RAISE NOTICE '==========================';
END $$;
