# ...existing code...

import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
# ...existing code...
from dotenv import load_dotenv
import os

# .env を明示的に UTF-8 で読み込む（存在すれば上書きする）
load_dotenv(dotenv_path=".env", encoding="utf-8")

# 環境変数値の余分なシングル/ダブルクォートを取り除く関数
def _env_get_clean(key):
    v = os.environ.get(key)
    if v is None:
        return None
    # 前後の単一/二重引用符を除去
    return v.strip().strip("'\"")

# 使用する接続パラメータを明示的に取得（サニタイズ）
DB_HOST = _env_get_clean("DB_HOST") or "localhost"
DB_USER = _env_get_clean("DB_USER") or "postgres"
DB_NAME = _env_get_clean("DB_NAME") or "codemon"
DB_PASSWORD = _env_get_clean("PGPASSWORD")

print("DEBUG: repr(DB_HOST) =", repr(DB_HOST))
print("DEBUG: repr(DB_USER) =", repr(DB_USER))
print("DEBUG: repr(DB_NAME) =", repr(DB_NAME))
print("DEBUG: repr(PGPASSWORD) =", repr(DB_PASSWORD))

# ...existing code...
# ここで psycopg2.connect に上で用意した変数を渡す
# conn = psycopg2.connect(host=DB_HOST, user=DB_USER, dbname=DB_NAME, password=DB_PASSWORD)
# ...existing code...
# Load .env in project root (UTF-8 で一回だけ読み込む／上書きされないよう統一)
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / '.env', encoding="utf-8")
SQL_DIR = BASE_DIR / "sql"
# 既に上でサニタイズ済みの DB_HOST/DB_USER/DB_NAME/DB_PASSWORD を優先して使う。
# 存在しなければ .env から取得してサニタイズする。
if 'DB_HOST' not in globals() or DB_HOST is None:
    DB_HOST = _env_get_clean("DB_HOST") or "localhost"
if 'DB_USER' not in globals() or DB_USER is None:
    DB_USER = _env_get_clean("DB_USER") or "postgres"
if 'DB_NAME' not in globals() or DB_NAME is None:
    DB_NAME = _env_get_clean("DB_NAME") or "codemon"

# パスワードは PGPASSWORD を優先、なければ DB_PASSWORD を使う
if 'DB_PASSWORD' not in globals() or DB_PASSWORD is None:
    DB_PASSWORD = _env_get_clean("PGPASSWORD") or _env_get_clean("DB_PASSWORD")

DB_PASS = DB_PASSWORD or ""
# ...existing code...


def read_sql(path: Path) -> str:
    for enc in ("utf-8", "cp932", "shift_jis", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")

# 明示的な実行順（必要に応じて順序を編集）
# ...existing code...
ordered = [
    "create_group.sql",        # group を先に作成
    "create_account.sql",
    "create_ai_config.sql",
    "create_ai_detail.sql",
    "create_system.sql",
    "create_algorithm.sql",
    "create_checklist.sql",
    "create_group_member.sql", # group_member は group と account の後
    "create_chat_history.sql",
    "create_ai_learning.sql",
]
# ...existing code...

def apply_sql_files():
    # 接続
    conn = psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS,
        options='-c client_encoding=UTF8'
    )
    try:
        with conn:
            with conn.cursor() as cur:
                for fname in ordered:
                    path = SQL_DIR / fname
                    if not path.exists():
                        print(f"Skipped (not found): {path}")
                        continue
                    print(f"Applying: {path.name} ...")
                    sql = read_sql(path)
                    cur.execute(sql)
                    print(f"Applied: {path.name}")
    finally:
        conn.close()

if __name__ == "__main__":
    apply_sql_files()
# ...existing code...