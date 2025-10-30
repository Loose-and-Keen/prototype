# db_utils.py
import sqlite3

DB_NAME = "aiken_user_data.db"

def init_db():
    """データベースとテーブルを初期化（なければ作成）"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # ユーザーテーブル (user_id は仮に固定で 'ken' とする MVP)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        name TEXT
    )
    """)
    # ユーザー目標テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_goals (
        user_id TEXT,
        goal TEXT, 
        FOREIGN KEY (user_id) REFERENCES users (user_id),
        PRIMARY KEY (user_id, goal) 
    )
    """)
    # MVP用に 'ken' ユーザーを作成 (初回のみ)
    try:
        cursor.execute("INSERT INTO users (user_id, name) VALUES (?, ?)", ('ken', 'Ken'))
    except sqlite3.IntegrityError:
        pass # 既に存在する場合は何もしない
    conn.commit()
    conn.close()

def get_user_goals(user_id='ken'):
    """指定されたユーザーの目標リストを取得"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT goal FROM user_goals WHERE user_id = ?", (user_id,))
    goals = [row[0] for row in cursor.fetchall()]
    conn.close()
    # もし目標が空なら、デフォルトとして基本的なものを返す (MVP用)
    if not goals:
        return ["basic_voice_control"] 
    return goals

def add_user_goal(user_id='ken', goal=""):
    """ユーザーに目標を追加"""
    if not goal:
        return
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO user_goals (user_id, goal) VALUES (?, ?)", (user_id, goal))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # 既に存在する場合は何もしない
    finally:
        conn.close()

def remove_user_goal(user_id='ken', goal=""):
     """ユーザーから目標を削除"""
     if not goal:
         return
     conn = sqlite3.connect(DB_NAME)
     cursor = conn.cursor()
     cursor.execute("DELETE FROM user_goals WHERE user_id = ? AND goal = ?", (user_id, goal))
     conn.commit()
     conn.close()

# --- 初期化実行 ---
# このファイルが読み込まれた時にDBがなければ作る
init_db()