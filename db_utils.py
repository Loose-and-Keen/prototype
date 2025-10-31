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
            ('money', '💰 投資', 3),
            ('fashion', '👕 ファッション', 4),
            ('love', '❤️ 恋愛', 5),
            ('beauty', '✨ 美容', 6),
            ('career', '💼 キャリア', 7)
        ]
        cursor.executemany("INSERT INTO M_Categories (category_id, category_name, sort_order) VALUES (?, ?, ?)", 
                           categories)

        # スマートホームの「経験値」を登録
        knowledge_data_smart_home = (
            'smart_home', 
            '家電を声操作できるようにしたい', 
            'SwitchBotハブと中古EchoでOK', 
            '拡張性が最強。将来カーテンも動かせるから、Nature Remoよりこっちがいい気がするよ', 
            '実は最初Nature Remo買って、カーテン自動化できなくて買い直したんだよな駄金だった（笑）',
            """
            **フェーズ1: 声の相棒 (予算: 〜3000円)**
            1. メルカリで「Amazon Echo Show (中古)」を探す
            2. ゲット！
            
            **フェーズ2: 家電ハック (予算: 〜3000円)**
            1. メルカリで「SwitchBot Hub Mini (中古)」を探す
            2. 設定して、テレビ・エアコンのリモコンを登録
            3. AlexaアプリでSwitchBotスキルを連携
            
            **フェーズ3: 声をかける**
            1. 「アレクサ、テレビつけて」
            """
        )
        
        # カテゴリ: money (お金)
        knowledge_data_money = (
            'money', 
            '投資って何から始めればいい？', 
            '楽天経済圏 + S&P500インデックス投資がお得な気がするよ', 
            'NISA/DCの税制優遇をフル活用し、手数料最安のS&P500で世界経済の成長に乗るのが、感情を排除した最短ルートだと思うな〜', 
            '個別株で一喜一憂してたけど、結局インデックス投資の「何もしない」が一番強いって気づいたんだよね（笑）', 
            """
            **フェーズ1: 「めんどくさい」を排除する口座開設**
            1. 「楽天銀行」「楽天証券」「楽天カード」を同時に申し込む。
            2. 証券口座で「つみたてNISA」と「iDeCo」を開設。
            
            **フェーズ2: 最強の設定（自動化）**
            1. 楽天カード決済で「eMAXIS Slim 米国株式(S&P500)」をNISA枠で満額（月10万）積み立てる設定をする
            2. iDeCoも同じ銘柄で満額設定
            
            **フェーズ3: 忘れる！**
            1. あとはマネーフォワードでたまに眺めるだけ。これが最強の投資な気がするな〜
            """
        )
        
        # カテゴリ: career (キャリア)
        knowledge_data_career = (
            'career',
            'PM（プロジェクトマネージャー）ってどうやったらなれる？',
            '「基本書1冊」と「WBS」が大事かな',
            'PMの仕事は「管理」じゃなくて、「ブラックボックスを可視化（WBS化）」して「完遂」、そしてお客さんを安心させることが大事だね',
            '最初はSEで、顧客の「こういうことっすか？」を言語化し続けてたら、自然とPMになってたんだよね（笑）',
            """
            **ステップ1: 知識のインストール**
            1. 『プロジェクトマネジメントの基本がぜんぶわかる本』みたいな薄い基本書を1冊だけ買って読む
            
            **ステップ2: 実践（WBS化）**
            1. 今やってる仕事（なんでもいい）を「WBS（やることリスト）」に分解する癖をつけるといいかも
            2. 「誰が」「いつまでに」「何を」やるのかを明確にしないとね
            
            **ステップ3: 報告**
            1. そのWBSを上司に見せて「こう進めようと思うんすけど、どうすか？」って「納得」を得たほうがいいね
            
            こんな感じでPMになれるんじゃないかな？
            """
        )
        
        # カテゴリ: love (恋愛)
        knowledge_data_love = (
            'love',
            'マッチングアプリ、めんどくさい…',
            '「バチェラーデート」一択な気がするよ',
            '普通のマッチングアプリは「アポ取るまで」が一番時間かかる。その「めんどくさい」を完全自動化できるのがバチェラーデートの最短ルート。',
            '何個かアプリ試したけど、結局アポ取るまでが一番疲れる笑　バチェラーデートはそこを全部AIに任せられるから楽だったな〜',
            """
            **最短ルートWBS:**
            1. バチェラーデートに登録。
            2. あとはAIが自動でアポ組んでくれるのを待つだけ。
            
            **【レート上げのパターンはこんな感じ笑**
            * **会話:** 相手の話に興味を持って聞くといいかも
            * **会計:** 奢ったほうがいい笑　カフェだしそんなに高くないから大丈夫
            * **連絡先:** デート後にLINE交換　しないと興味持たれなかったと思われて点数下がる笑
            
            まぁ、めんどくさいことはAIに任せた方が楽だね笑
            """
        )

        # カテゴリ: beauty (美容)
        knowledge_data_beauty = (
            'beauty',
            '男のスキンケア、何からやればいい？',
            '「美容液」一点集中投資と「髭脱毛」での根本解決',
            '化粧水とか乳液とか色々やるのは「めんどくさい」笑 大事なのは「保湿」と「強力な成分」。だから安いパック＋美容液（成分）＋ニベア（保湿）でOK。',
            '俺も色々試したけど、結局この形に落ち着いたわ。髭脱毛（ヤグレーザー8回で十分！）はほんとに楽だし清潔感でるよ、朝の時間が5分は大事だよね笑',
            """
            **ステップ1: 日常ケア（習慣化）**
            1. 毎晩、安い大容量パック（アマゾンで適当に）する
            2. 終わったら、ちょっといい「いい美容液」（ナイルとか）を塗る
            3. 最後にニベアでフタをすると保湿完璧
            
            **ステップ2: 根本解決（髭脱毛）**
            1. ヤグレーザー（YAG）一択。医療脱毛で「ヤグで」って指定するといいよ
            2. 8回もやれば全然違う、毎朝髭剃りの手間が省けて楽になるよ
            """
        )
        
        # カテゴリ: fashion (ファッション)
        knowledge_data_fashion = (
            'fashion',
            '服選ぶのめんどくさい…',
            '「仕事着の固定化」と「私服のトレンド把握」は分けるといいかも',
            '毎日服選ぶ時間こそ人生の無駄な気がするからさ、仕事着は「ノンアイロンジャージシャツ（白）」で固定。これで考える手間が省けるよ、アイロンもいらないし笑',
            '前は色々悩んでたけど、これにしてから本当に楽だよ',
            """
            **WBS: 仕事着の最短ルート**
            1. ユニクロか無印で「ノンアイロンジャージシャツ（白）」を5枚買う
            2. ズボンは紺のスラックスが無難かなー　グレーだとシミが目立つ気がする笑
            
            **WBS: 私服の最短ルート**
            1. GUか街中で「今っぽいな」ってトレンドを把握する。
            2. 「Shein（シーイン）」のアプリで、人気ランキング上位の安いやつを買う
            3. これでOK。失敗しても安いから痛くない笑
            """
        )

        # DBにまとめてINSERT！
        all_knowledge_data = [
            knowledge_data_smart_home,
            knowledge_data_money,
            knowledge_data_career,
            knowledge_data_love,
            knowledge_data_beauty,
            knowledge_data_fashion
        ]
        
        cursor.executemany("""
        INSERT INTO M_Knowledge_Base 
            (category_id, preset_question, success_title, success_why, failure_experience, wbs_data) 
        VALUES (?, ?, ?, ?, ?, ?)
        """, all_knowledge_data)
        
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

def get_user_goals_by_category(user_id, category_id):
    """指定されたユーザー/カテゴリの目標リストとステータスを取得"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # T_User_Goals から goal_key と status を取得
    cursor.execute("SELECT goal_key, status FROM T_User_Goals WHERE user_id = ? AND category_id = ?", (user_id, category_id))
    goals = cursor.fetchall() # [(goal_key, status), ...]
    conn.close()
    
    # --- MVP用：もしT_User_Goalsにまだ目標がなかったら、M_Knowledge_Baseから作ってあげる ---
    if not goals:
        # M_Knowledge_Base から goal_key (preset_questionで代用) を取得
        cursor = sqlite3.connect(DB_NAME).cursor()
        cursor.execute("SELECT preset_question FROM M_Knowledge_Base WHERE category_id = ?", (category_id,))
        preset_goals = cursor.fetchall()
        
        new_goals_to_insert = []
        for (question,) in preset_goals:
            # T_User_Goals に 'not_started' で追加
            new_goals_to_insert.append((user_id, category_id, question, 'not_started'))
        
        if new_goals_to_insert:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            try:
                cursor.executemany("INSERT INTO T_User_Goals (user_id, category_id, goal_key, status) VALUES (?, ?, ?, ?)", 
                                   new_goals_to_insert)
                conn.commit()
            except sqlite3.IntegrityError:
                pass # 念のため
            finally:
                conn.close()
        
        # もう一度DBから取得
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT goal_key, status FROM T_User_Goals WHERE user_id = ? AND category_id = ?", (user_id, category_id))
        goals = cursor.fetchall()
        conn.close()
        
    return goals

def update_user_goal_status(user_id, goal_key, status):
    """ユーザーの目標ステータスを更新"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE T_User_Goals SET status = ? WHERE user_id = ? AND goal_key = ?", (status, user_id, goal_key))
    conn.commit()
    conn.close()