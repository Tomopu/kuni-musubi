from sqlalchemy import Engine, bindparam, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Integer, String, Text


DEV_SCHEMA_STATEMENTS = [
    # parties
    "ALTER TABLE parties ADD COLUMN IF NOT EXISTS color_hex VARCHAR(7)",
    "ALTER TABLE parties ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true",
    "ALTER TABLE parties ADD COLUMN IF NOT EXISTS display_order INTEGER DEFAULT 0",
    "ALTER TABLE parties ADD COLUMN IF NOT EXISTS founded_year INTEGER",
    "ALTER TABLE parties ADD COLUMN IF NOT EXISTS leader_name VARCHAR(100)",
    "ALTER TABLE parties ADD COLUMN IF NOT EXISTS house_of_representatives_seats INTEGER",
    "ALTER TABLE parties ADD COLUMN IF NOT EXISTS house_of_councillors_seats INTEGER",
    "ALTER TABLE parties ADD COLUMN IF NOT EXISTS ideology_summary TEXT",
    "ALTER TABLE parties ADD COLUMN IF NOT EXISTS manifesto_summary TEXT",
    "ALTER TABLE parties ADD COLUMN IF NOT EXISTS manifesto_promises TEXT[] DEFAULT '{}'",
    "ALTER TABLE parties ADD COLUMN IF NOT EXISTS main_policy_categories TEXT[] DEFAULT '{}'",
    "ALTER TABLE parties ADD COLUMN IF NOT EXISTS official_url VARCHAR(2048)",
    "ALTER TABLE parties ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now()",
    "ALTER TABLE parties ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now()",
    # policy_categories
    "ALTER TABLE policy_categories ADD COLUMN IF NOT EXISTS slug VARCHAR(100)",
    "ALTER TABLE policy_categories ADD COLUMN IF NOT EXISTS description TEXT",
    "ALTER TABLE policy_categories ADD COLUMN IF NOT EXISTS display_order INTEGER DEFAULT 0",
    "ALTER TABLE policy_categories ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now()",
    "ALTER TABLE policy_categories ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now()",
    # articles
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS original_title VARCHAR(500)",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS source_type VARCHAR(50)",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS primary_source_url TEXT",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS published_at TIMESTAMPTZ NOT NULL DEFAULT now()",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS collected_at TIMESTAMPTZ",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'draft'",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS important_rank INTEGER",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS is_published BOOLEAN DEFAULT false",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now()",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now()",
    # raw_content カラム追加
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS raw_content TEXT",
    # primary_source_url の重複排除 → ユニークインデックス作成
    """
DO $$
BEGIN
    -- 重複 URL がある場合、最新レコード1件を残して削除する
    DELETE FROM articles
    WHERE id NOT IN (
        SELECT DISTINCT ON (primary_source_url) id
        FROM articles
        WHERE primary_source_url IS NOT NULL
        ORDER BY primary_source_url, created_at DESC
    )
    AND primary_source_url IS NOT NULL;

    -- ユニークインデックスがなければ作成する（NULL は除外）
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'articles'
          AND indexname = 'uq_articles_primary_source_url'
    ) THEN
        CREATE UNIQUE INDEX uq_articles_primary_source_url
        ON articles (primary_source_url)
        WHERE primary_source_url IS NOT NULL;
    END IF;
END
$$;
""",
    # article_display_contents
    "ALTER TABLE article_display_contents ADD COLUMN IF NOT EXISTS display_title VARCHAR(300) NOT NULL DEFAULT ''",
    "ALTER TABLE article_display_contents ADD COLUMN IF NOT EXISTS card_summary TEXT NOT NULL DEFAULT ''",
    "ALTER TABLE article_display_contents ADD COLUMN IF NOT EXISTS thumbnail_type VARCHAR(50)",
    "ALTER TABLE article_display_contents ADD COLUMN IF NOT EXISTS thumbnail_text TEXT",
    "ALTER TABLE article_display_contents ADD COLUMN IF NOT EXISTS thumbnail_url TEXT",
    "ALTER TABLE article_display_contents ADD COLUMN IF NOT EXISTS thumbnail_alt_text TEXT",
    "ALTER TABLE article_display_contents ADD COLUMN IF NOT EXISTS positive_point TEXT NOT NULL DEFAULT ''",
    "ALTER TABLE article_display_contents ADD COLUMN IF NOT EXISTS life_impact TEXT NOT NULL DEFAULT ''",
    "ALTER TABLE article_display_contents ADD COLUMN IF NOT EXISTS remaining_issues TEXT NOT NULL DEFAULT '[]'",
    "ALTER TABLE article_display_contents ADD COLUMN IF NOT EXISTS public_reactions_summary TEXT",
    "ALTER TABLE article_display_contents ADD COLUMN IF NOT EXISTS created_by VARCHAR(50)",
    "ALTER TABLE article_display_contents ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now()",
    "ALTER TABLE article_display_contents ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now()",
    # article_sources
    "ALTER TABLE article_sources ADD COLUMN IF NOT EXISTS source_name TEXT",
    "ALTER TABLE article_sources ADD COLUMN IF NOT EXISTS source_type VARCHAR(50)",
    "ALTER TABLE article_sources ADD COLUMN IF NOT EXISTS published_at TIMESTAMPTZ",
    "ALTER TABLE article_sources ADD COLUMN IF NOT EXISTS retrieved_at TIMESTAMPTZ",
    "ALTER TABLE article_sources ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now()",
    # article_parties
    "ALTER TABLE article_parties ADD COLUMN IF NOT EXISTS relation_type VARCHAR(20) NOT NULL DEFAULT 'primary'",
    "ALTER TABLE article_parties ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now()",
    # article_categories
    "ALTER TABLE article_categories ADD COLUMN IF NOT EXISTS display_order INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE article_categories ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now()",
    # onboarding_events
    "ALTER TABLE onboarding_events ADD COLUMN IF NOT EXISTS selected_party_status VARCHAR(20)",
    # daily_article_stats
    (
        "ALTER TABLE daily_article_stats "
        "ADD COLUMN IF NOT EXISTS unhelpful_click_count INTEGER DEFAULT 0"
    ),
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint
            WHERE conname = 'daily_article_stats_article_id_stat_date_key'
        ) THEN
            ALTER TABLE daily_article_stats
            ADD CONSTRAINT daily_article_stats_article_id_stat_date_key
            UNIQUE (article_id, stat_date);
        END IF;
    END
    $$;
    """,
]

DEV_SCHEMA_TABLES = [
    "parties",
    "policy_categories",
    "articles",
    "article_display_contents",
    "article_sources",
    "article_parties",
    "article_categories",
    "onboarding_events",
    "article_events",
    "daily_article_stats",
    "daily_category_stats",
    "import_jobs",
    "import_job_logs",
]


def _validate_identifier(identifier: str) -> str:
    if not identifier.replace("_", "").isalnum() or not identifier[0].isalpha():
        raise ValueError(f"Unsafe SQL identifier: {identifier}")
    return identifier


def _drop_not_null_for_legacy_columns(engine: Engine) -> None:
    from app.infrastructure.db.models import Base

    model_columns_by_table = {
        table_name: {column.name for column in table.columns}
        for table_name, table in Base.metadata.tables.items()
    }

    with engine.begin() as connection:
        rows = connection.execute(
            text(
                """
                SELECT table_name, column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name IN :table_names
                  AND is_nullable = 'NO'
                """
            ).bindparams(bindparam("table_names", expanding=True)),
            {"table_names": DEV_SCHEMA_TABLES},
        )

        for table_name, column_name in rows:
            model_columns = model_columns_by_table.get(table_name, set())
            if column_name in model_columns:
                continue

            safe_table = _validate_identifier(table_name)
            safe_column = _validate_identifier(column_name)
            connection.execute(
                text(
                    f"ALTER TABLE {safe_table} ALTER COLUMN {safe_column} DROP NOT NULL"
                )
            )


def _column_type_sql(column_type: object) -> str:
    if isinstance(column_type, UUID):
        return "UUID"
    if isinstance(column_type, ARRAY):
        return "TEXT[]"
    if isinstance(column_type, String):
        return f"VARCHAR({column_type.length})" if column_type.length else "VARCHAR"
    if isinstance(column_type, Text):
        return "TEXT"
    if isinstance(column_type, Integer):
        return "INTEGER"
    if isinstance(column_type, Boolean):
        return "BOOLEAN"
    if isinstance(column_type, DateTime):
        return "TIMESTAMPTZ" if column_type.timezone else "TIMESTAMP"
    return "TEXT"


def _add_missing_model_columns(engine: Engine) -> None:
    from app.infrastructure.db.models import Base

    with engine.begin() as connection:
        existing_rows = connection.execute(
            text(
                """
                SELECT table_name, column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name IN :table_names
                """
            ).bindparams(bindparam("table_names", expanding=True)),
            {"table_names": DEV_SCHEMA_TABLES},
        )
        existing_columns = {
            (table_name, column_name) for table_name, column_name in existing_rows
        }

        for table_name, table in Base.metadata.tables.items():
            if table_name not in DEV_SCHEMA_TABLES:
                continue
            safe_table = _validate_identifier(table_name)
            for column in table.columns:
                if (table_name, column.name) in existing_columns:
                    continue
                safe_column = _validate_identifier(column.name)
                connection.execute(
                    text(
                        f"ALTER TABLE {safe_table} "
                        f"ADD COLUMN IF NOT EXISTS {safe_column} "
                        f"{_column_type_sql(column.type)}"
                    )
                )


def ensure_dev_schema(engine: Engine) -> None:
    """Keep existing development DB volumes compatible with the current models.

    SQLAlchemy create_all creates missing tables, but it does not alter tables that
    already exist. This lightweight sync is for local Docker development only; a
    production deployment should use real Alembic migrations.
    """
    with engine.begin() as connection:
        for statement in DEV_SCHEMA_STATEMENTS:
            connection.execute(text(statement))
    _add_missing_model_columns(engine)
    _drop_not_null_for_legacy_columns(engine)
