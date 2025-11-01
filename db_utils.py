# db_utils.py (スリム化DAOバージョン)
import sqlite3

DB_NAME = "aiken_user_data.db" # 接続先のファイル名はこれ

def get_db_connection():
    """DB接続を返す（おまじない）"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # カラム名でアクセスできるようにしとくと便利
    return conn

def get_categories():
    """タブに表示するカテゴリを全部持ってくる"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, category_name FROM M_Categories ORDER BY sort_order")
    categories = cursor.fetchall() # [(id, name), (id, name), ...]
    conn.close()
    return categories

def get_preset_questions(category_id):
    """指定されたカテゴリのプリセット質問（ボタン用）を持ってくる"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT preset_question, knowledge_id FROM M_Knowledge_Base WHERE category_id = ?", (category_id,))
    questions = cursor.fetchall() # [(question, id), (question, id), ...]
    conn.close()
    return questions

def get_knowledge_details_by_id(knowledge_id):
    """指定されたIDの「経験値の詳細（箇条書きDB）」を持ってくる (RAG用)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # success_titleもKnowledge_Baseから一緒に取得
    cursor.execute("""
        SELECT 
            kb.success_title,
            kd.fact_type,
            kd.fact_text,
            kd.experience_flag
        FROM M_Knowledge_Details kd
        JOIN M_Knowledge_Base kb ON kd.knowledge_id = kb.knowledge_id
        WHERE kd.knowledge_id = ?
        ORDER BY kd.sort_order
    """, (knowledge_id,))
    details = cursor.fetchall() # [(title, type, text, flag), ...]
    conn.close()
    return details

def get_user_goals_by_category(user_id, category_id):
    """指定されたユーザー/カテゴリの目標リストとステータスを取得"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT goal_key, status FROM T_User_Goals WHERE user_id = ? AND category_id = ?", (user_id, category_id))
    goals = cursor.fetchall()
    conn.close()
    
    # --- MVP用：もしT_User_Goalsにまだ目標がなかったら、M_Knowledge_Baseから作ってあげる ---
    if not goals:
        cursor = get_db_connection().cursor()
        cursor.execute("SELECT preset_question FROM M_Knowledge_Base WHERE category_id = ?", (category_id,))
        preset_goals = cursor.fetchall()
        
        new_goals_to_insert = []
        for row in preset_goals:
            goal_key = row['preset_question'] # preset_questionをgoal_keyとして使う
            new_goals_to_insert.append((user_id, category_id, goal_key, 'not_started'))
        
        if new_goals_to_insert:
            conn_insert = get_db_connection()
            cursor_insert = conn_insert.cursor()
            try:
                cursor_insert.executemany("INSERT INTO T_User_Goals (user_id, category_id, goal_key, status) VALUES (?, ?, ?, ?)", 
                                          new_goals_to_insert)
                conn_insert.commit()
            except sqlite3.IntegrityError:
                pass 
            finally:
                conn_insert.close()
        
        # もう一度DBから取得
        conn_retry = get_db_connection()
        cursor_retry = conn_retry.cursor()
        cursor_retry.execute("SELECT goal_key, status FROM T_User_Goals WHERE user_id = ? AND category_id = ?", (user_id, category_id))
        goals = cursor_retry.fetchall()
        conn_retry.close()
        
    return goals

def update_user_goal_status(user_id, goal_key, status):
    """ユーザーの目標ステータスを更新"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE T_User_Goals SET status = ? WHERE user_id = ? AND goal_key = ?", (status, user_id, goal_key))
    conn.commit()
    conn.close()