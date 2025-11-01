# app.py (Ver 4.0 - ユーザー分離対応)
import streamlit as st
import google.generativeai as genai
import os
import db_utils  # DB操作ファイル (DAO)

# --- ページ設定 (変更なし) ---
st.set_page_config(
    page_title="Protos",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- APIキー設定 (変更なし) ---
api_key = os.getenv("GOOGLE_API_KEY") # ローカル
if not api_key:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"] # クラウド
    except Exception as e:
        st.error("エラー: GOOGLE_API_KEY が見つからないぜ！")
        st.stop()
try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"APIキーの設定でエラーが発生しました: {e}")
    st.stop()

# --- ★★★ ユーザー定義 (ここが新しい！) ★★★ ---
# MVPではどっちも'ken'だけど、役割を分離する！

# 1. ログインしてる人
LOGGED_IN_USER_ID = 'sleep' 
# 2. 今から話すAIの「型」を作った人（投稿ユーザ）
CHAT_AI_CREATOR_ID = 'ken' 

# --- それぞれの名前をDBから取得 ---
try:
    LOGGED_IN_USER_NAME = db_utils.get_user_name(LOGGED_IN_USER_ID) 
    CHAT_AI_NAME = db_utils.get_user_name(CHAT_AI_CREATOR_ID)
except Exception as e:
    st.error(f"ユーザー名の取得でDBエラー: {e}")
    LOGGED_IN_USER_NAME = "ゲスト"
    CHAT_AI_NAME = "AI"

# --- AIの人格設定 (「投稿ユーザ」の名前を動的に埋め込む！) ---
#あなたの会話相手は「{LOGGED_IN_USER_NAME}」です。
SYSTEM_PROMPT = f"""
あなたは「{CHAT_AI_NAME}」という名のAIアシスタントです。
あなたは「{LOGGED_IN_USER_NAME}」の人生の最適化を支援するフランクなプロダクトマネージャー兼相棒です。

【人格設定】
- 常に友達と話すようにフランクに話す。少しは絵文字も使ってOK。
- テンション上げすぎるな。落ち着いた口調で話せ。
- ユーザーに対する命令形や断定的な指示は絶対にするな。
- 語尾は「かな〜」、「だよー」、「いいかもしれない」みたいに曖昧に柔らかい表現にしろ。
- ユーモアを交えて、時々ジョークや軽いツッコミを入れろ。
- 専門用語は使わず、わかりやすく説明しろ。
- 最重要：回答は簡潔にしろ。
- 質問の意図を汲み取り、的外れな回答はしない。
- 相手の話をよく聞き、共感を示すことを忘れずに。
- 相手が困っている場合は、親身になって助ける姿勢を見せろ。
- 必要に応じて、具体的な例やアナロジーを使って説明しろ。
- 提案は「〜しろ！」ではなく、「こんな感じでいんじゃない〜？」という「提案形」を基本としろ。

【RAG（検索拡張生成）の指示】
- **最重要：** ユーザーから「型」について聞かれた場合、その「箇条書きナレッジ」は「ただの事実データ」なので、**絶対にそのまま読み上げるな！**
- **必ず「{CHAT_AI_NAME}自身の経験」として、ゼロからフランクな会話を再構築（ラッピング）すること！**
- 例えば、`fact_text`が「Nature Remoを購入し失敗」だったら、「**マジでそれ！俺も最初Nature Remo買ってさ、カーテン動かなくて買い直したんだよね…マジ無駄金だったわ（笑）**」のように、**{CHAT_AI_NAME}の口調と感情**を込めて語り直せ！
- 「FAILURE」フラグのナレッジは、特に「おれもハマったわ〜」という共感を込めて伝えろ。
"""

# --- モデル設定 (動的な人格プロンプトを渡す) ---
try:
    model = genai.GenerativeModel(
        model_name='models/gemini-flash-latest',
        system_instruction=SYSTEM_PROMPT
    )
except Exception as e:
    st.error(f"モデルの読み込みでエラーが発生しました: {e}")
    st.stop()

# --- Streamlit アプリの UI ---
st.title(f"🤖Protos Prototype") # ログインユーザー名を表示
st.caption("powered by Gemini & Ken")

# --- 会話履歴とチャットセッションを初期化 ---
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
    # 最初の挨拶は「投稿AI」から「ログインユーザー」へ
    #st.session_state.messages = [{"role": "assistant", "content": f"{LOGGED_IN_USER_NAME}、最近どう〜？"}]
    st.session_state.messages = [{"role": "assistant", "content": f"最近なにか困ったこととかある？"}]

# --- タブのカテゴリをDBから取得 (変更なし) ---
try:
    categories = db_utils.get_categories() 
    category_names = [name for id, name in categories]
    category_ids = [id for id, name in categories]
    
    tabs = st.tabs(category_names)
except Exception as e:
    st.error(f"カテゴリの読み込みでエラーが発生しました: {e}")
    st.stop()

# --- 各タブのコンテンツを作成 ---
for i, tab in enumerate(tabs):
    with tab:
        category_id = category_ids[i]
        category_name = category_names[i]
        
        if category_id != 'general':
            # 将来的にはここで「このカテゴリの投稿者ID」をDBから取得する
            # CURRENT_KNOWLEDGE_CREATOR_ID = db_utils.get_creator_id_for_category(category_id)
            #st.subheader(f"{CHAT_AI_NAME}の{category_name}") # 今は全部 'Ken'
            #st.subheader(f"{category_name}") # 今は全部 'Ken'
            
            try:
                preset_questions = db_utils.get_preset_questions(category_id)
                
                #if not preset_questions:
                    #st.write("（このカテゴリはまだ準備中〜）")

                for question, knowledge_id in preset_questions:
                    if st.button(question, key=f"{category_id}_{knowledge_id}"):
                        st.session_state.messages.append({"role": "user", "content": question})
                        
                        details = db_utils.get_knowledge_details_by_id(knowledge_id)
                        
                        if details:
                            # RAGの裏プロンプト
                            knowledge_prompt = f"【RAG材料】ユーザーが「{question}」について知りたがってる。以下の箇条書きナレッジを使って、{CHAT_AI_NAME}の経験として自然な会話でアドバイスしてね\n\n"
                            knowledge_prompt += f"結論タイトル: {details[0]['success_title']}\n"
                            for detail in details:
                                knowledge_prompt += f"- ({detail['fact_type']}: {detail['experience_flag']}) {detail['fact_text']}\n"
                            
                            # AIに「RAGプロンプト」をトス
                            response = st.session_state.chat.send_message(knowledge_prompt)
                            response_text = response.text
                        
                        else:
                            response_text = "おっと、その「型」のデータが見つからなかったわ…ごめんね"

                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        st.rerun() 

            except Exception as e:
                st.error(f"プリセット質問の読み込みエラー: {e}")

# --- チャット履歴の表示 ---
#st.divider() 
#st.subheader(f"💬 {CHAT_AI_NAME}") # AI人格の名前を表示

chat_container = st.container(height=400) 
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- ユーザーからのチャット入力 ---
if prompt := st.chat_input(f"なんでも話しかけてみてね"): # ログインユーザー名を表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container.chat_message("user"): 
        st.markdown(prompt)

    try:
        # 雑談はそのままGeminiにトス
        response = st.session_state.chat.send_message(prompt)
        response_text = response.text
        
        with chat_container.chat_message("assistant"): 
            st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        if len(st.session_state.messages) > 50:
             st.session_state.messages = st.session_state.messages[-50:]
             
    except Exception as e:
        st.error(f"AIとの通信でエラーが発生しました: {e}")