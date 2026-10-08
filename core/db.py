import random
import sqlite3

from flask import current_app, g
from werkzeug.security import generate_password_hash

from core.app_settings import ADMIN_SETTINGS


ADMIN_USERNAME = ADMIN_SETTINGS.username
ADMIN_PASSWORD = ADMIN_SETTINGS.password


def _generate_db_uuid(db, used_values):
    for _ in range(2000):
        candidate = random.randint(100, 999)
        if candidate not in used_values:
            used_values.add(candidate)
            return candidate
    raise RuntimeError("历史用户 UUID 迁移失败")


def get_db():
    """Return a per-request SQLite connection."""
    db = getattr(g, "_database", None)
    if db is None:
        database = current_app.config["DATABASE"]
        db = g._database = sqlite3.connect(database)
        db.row_factory = sqlite3.Row
    return db


def close_db(exception=None):
    """Close the request-scoped connection if it exists."""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db(app):
    """Ensure the SQLite schema exists and register teardown hooks."""
    app.config.setdefault("DATABASE", "stock.db")

    app.teardown_appcontext(close_db)

    with app.app_context():
        db = sqlite3.connect(app.config["DATABASE"])
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid INTEGER UNIQUE,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                report_schedule_enabled INTEGER DEFAULT 0,
                report_schedule_time TEXT,
                report_schedule_stock_codes TEXT,
                report_schedule_last_sent_at TEXT,
                avatar_path TEXT,
                avatar_name TEXT,
                approval_status TEXT DEFAULT 'approved',
                is_admin INTEGER DEFAULT 0
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS user_stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                stock_code TEXT NOT NULL,
                stock_name TEXT NOT NULL,
                add_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE (user_id, stock_code)
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS report_histories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                stock_code TEXT NOT NULL,
                stock_name TEXT,
                report_title TEXT,
                report_html TEXT NOT NULL,
                report_context_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS email_verification_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                code TEXT NOT NULL,
                purpose TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                verified INTEGER DEFAULT 0,
                attempt_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS forum_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                image_path TEXT,
                image_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS forum_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES forum_posts (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS forum_post_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES forum_posts (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE (post_id, user_id)
            )
            """
        )
        columns = [row[1] for row in db.execute("PRAGMA table_info(users)").fetchall()]
        if "email" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN email TEXT")
        if "llm_system_prompt" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN llm_system_prompt TEXT")
        if "llm_user_prompt" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN llm_user_prompt TEXT")
        if "uuid" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN uuid INTEGER")
        if "is_admin" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        if "report_schedule_enabled" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN report_schedule_enabled INTEGER DEFAULT 0")
        if "report_schedule_time" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN report_schedule_time TEXT")
        if "report_schedule_stock_codes" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN report_schedule_stock_codes TEXT")
        if "report_schedule_last_sent_at" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN report_schedule_last_sent_at TEXT")
        if "approval_status" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN approval_status TEXT DEFAULT 'approved'")
        if "avatar_path" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN avatar_path TEXT")
        if "avatar_name" not in columns:
            db.execute("ALTER TABLE users ADD COLUMN avatar_name TEXT")
        forum_columns = [row[1] for row in db.execute("PRAGMA table_info(forum_posts)").fetchall()]
        if "image_path" not in forum_columns:
            db.execute("ALTER TABLE forum_posts ADD COLUMN image_path TEXT")
        if "image_name" not in forum_columns:
            db.execute("ALTER TABLE forum_posts ADD COLUMN image_name TEXT")

        verification_columns = [
            row[1] for row in db.execute("PRAGMA table_info(email_verification_codes)").fetchall()
        ]
        if "attempt_count" not in verification_columns:
            db.execute(
                "ALTER TABLE email_verification_codes ADD COLUMN attempt_count INTEGER DEFAULT 0"
            )

        if not ADMIN_PASSWORD:
            raise RuntimeError("必须通过 ADMIN_PASSWORD 环境变量配置管理员密码")

        admin_password_hash = generate_password_hash(ADMIN_PASSWORD)
        existing_admin = db.execute("SELECT id FROM users WHERE username = ?", (ADMIN_USERNAME,)).fetchone()
        if existing_admin:
            db.execute(
                "UPDATE users SET uuid = ?, password = ?, is_admin = ?, approval_status = ? WHERE username = ?",
                (1, admin_password_hash, 1, "approved", ADMIN_USERNAME),
            )
        else:
            db.execute(
                "INSERT INTO users (uuid, username, password, is_admin, approval_status) VALUES (?, ?, ?, ?, ?)",
                (1, ADMIN_USERNAME, admin_password_hash, 1, "approved"),
            )
        db.execute("UPDATE users SET approval_status = ? WHERE approval_status IS NULL OR approval_status = ''", ("approved",))

        used_uuids = {
            int(row[0])
            for row in db.execute("SELECT uuid FROM users WHERE uuid IS NOT NULL").fetchall()
            if row[0] is not None
        }
        legacy_rows = db.execute(
            "SELECT id FROM users WHERE (uuid IS NULL OR uuid = '') AND username != ? ORDER BY id ASC",
            (ADMIN_USERNAME,),
        ).fetchall()
        for row in legacy_rows:
            db.execute(
                "UPDATE users SET uuid = ? WHERE id = ?",
                (_generate_db_uuid(db, used_uuids), row[0]),
            )
        db.commit()
        db.close()
