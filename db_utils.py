# db_utils.py
import sqlite3

DB_NAME = "aiken_user_data.db" # これがDBファイル本体の名前になる

def init_db():
    """
    データベースとテーブルを初期化（なければ作成）する。
    「思考OS」のマスターテーブルもここで定義するぜ！
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # --- 1. ユーザーマスター ---
    # MVPでは 'ken' ユーザー固定だけど、将来のプラットフォーム化を見据えて作る
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS M_Users (
        user_id TEXT PRIMARY KEY,
        user_name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        plan_type TEXT DEFAULT 'free' NOT NULL 
    )
    """)

    # --- 2. カテゴリマスター (タブUI用) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS M_Categories (
        category_id TEXT PRIMARY KEY,
        category_name TEXT NOT NULL,
        sort_order INTEGER
    )
    """)

    # --- 3. Kenの経験値DB (「思考OS」の本体！) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS M_Knowledge_Base (
        knowledge_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id TEXT NOT NULL,
        preset_question TEXT NOT NULL,
        success_title TEXT,
        success_why TEXT,
        failure_experience TEXT,
        wbs_data TEXT,
        FOREIGN KEY (category_id) REFERENCES M_Categories (category_id)
    )
    """)
    
    # --- 4. ユーザーごとの目標/進捗 (人生RPG用) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS T_User_Goals (
        user_goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        category_id TEXT NOT NULL,
        goal_key TEXT NOT NULL,
        status TEXT DEFAULT 'not_started' NOT NULL,
        FOREIGN KEY (user_id) REFERENCES M_Users (user_id),
        FOREIGN KEY (category_id) REFERENCES M_Categories (category_id)
    )
    """)

    # --- MVP用の初期データ投入 (初回のみ実行される) ---
    try:
        # MVPユーザー 'ken' を作成
        cursor.execute("INSERT INTO M_Users (user_id, user_name, password_hash) VALUES (?, ?, ?)", 
                       ('ken', 'Ken', 'dummy_hash')) # パスワードは後でちゃんと実装する
        
        # カテゴリタブを登録
        categories = [
            ('general', '💬 雑談', 1),
            ('smart_home', '🏠 スマートホーム', 2),
            ('money', '💰 お金・投資', 3),
            ('fashion', '👕 ファッション', 4),
            ('love', '❤️ 恋愛', 5),
            ('beauty', '✨ 美容', 6),
            ('career', '💼 キャリア', 7)
        ]
        cursor.executemany("INSERT INTO M_Categories (category_id, category_name, sort_order) VALUES (?, ?, ?)", 
                           categories)

        # スマートホームの「経験値」を登録
        knowledge_data = (
            'smart_home', 
            '5000円で声操作できるようにしたい！', 
            'SwitchBotハブと中古EchoでOK', 
            '拡張性が最強。将来カーテンも動かせるから、Nature Remoよりこっちが最短ルート。', 
            '俺は最初Nature Remo買って、カーテン自動化できなくて買い直したんだよな…無駄金だったぜ！', 
            # WBSデータ (本当はもっと構造化するけど、MVPではテキストで)
            """
            **フェーズ1: 声の相棒 (予算: 〜3000円)**
            1. メルカリで「Amazon Echo Show (中古)」を探す！
            2. ゲット！
            
            **フェーズ2: 家電ハック (予算: 〜3000円)**
            1. メルカリで「SwitchBot Hub Mini (中古)」を探す！
            2. 設定して、テレビ・エアコンのリモコンを登録！
            3. AlexaアプリでSwitchBotスキルを連携！
            
            **フェーズ3: 叫ぶ！**
            1. 「アレクサ、テレビつけて！」
            """
        )
        cursor.execute("""
        INSERT INTO M_Knowledge_Base 
            (category_id, preset_question, success_title, success_why, failure_experience, wbs_data) 
        VALUES (?, ?, ?, ?, ?, ?)
        """, knowledge_data)

    except sqlite3.IntegrityError:
        # データが既に存在する場合は何もしない (初回起動時のみ実行されるため)
        pass 

    conn.commit()
    conn.close()
    print("AI-Ken データベースの初期化が完了したぜ！")

# --- DB操作関数 (app.py から呼び出す用) ---

def get_categories():
    """タブに表示するカテゴリを全部持ってくる"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, category_name FROM M_Categories ORDER BY sort_order")
    categories = cursor.fetchall() # [(id, name), (id, name), ...]
    conn.close()
    return categories

def get_preset_questions(category_id):
    """指定されたカテゴリのプリセット質問（ボタン用）を持ってくる"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT preset_question, knowledge_id FROM M_Knowledge_Base WHERE category_id = ?", (category_id,))
    questions = cursor.fetchall() # [(question, id), (question, id), ...]
    conn.close()
    return questions

def get_knowledge_by_id(knowledge_id):
    """指定されたIDの「経験値（WBSや失敗談）」を持ってくる"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT success_title, success_why, failure_experience, wbs_data FROM M_Knowledge_Base WHERE knowledge_id = ?", (knowledge_id,))
    knowledge = cursor.fetchone() # (title, why, failure, wbs)
    conn.close()
    return knowledge

# ---
# このファイルがインポートされた時、または直接実行された時に
# データベースがなければ自動で作る
# ---
init_db()