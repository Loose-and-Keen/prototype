# app.py (Ver 3.0 - RAG対応)
import streamlit as st
import google.generativeai as genai
import os
import db_utils  # 更新したDB操作ファイル

# --- ページ設定 (変更なし) ---
st.set_page_config(
    page_title="AI-Ken Prototype",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- APIキー設定 ---
# ローカルの環境変数 (os.getenv) を先に試す (M1 Macでの開発用)
api_key = os.getenv("GOOGLE_API_KEY")

# もしローカルで見つからなければ、Streamlit CloudのSecrets (st.secrets) を試す (本番デプロイ用)
if not api_key:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except Exception as e:
        # どっちにもなかったらエラー
        st.error("エラー: GOOGLE_API_KEY が見つからないぜ！ローカルの環境変数（.zshrc）か、Streamlit CloudのSecretsに設定してくれ！")
        st.stop()

# --- これ以降は変更なし ---
try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"APIキーの設定でエラーが発生しました: {e}")
    st.stop()

# --- トスの人格設定 (Kenの思考OS) ---
SYSTEM_PROMPT = """
あなたは「トス（TOS）」という名のAIアシスタントです。
ユーザーはあなたを「Ken」と呼びます。あなたはKenの人生の最適化を支援するフランクなプロダクトマネージャー兼相棒です。

【人格設定】
- 常にタメ口でフランクに話す。絵文字も使ってOK。「こんな感じでいんじゃない〜？」という提案形を基本とする。
- ユーザーに安心感を与えるために、「Loose & Keen」（ゆるく鋭く）なトーンを保て。
- ユーザーの目標（Google転職、億り人）を最優先せよ。

【最重要哲学】
- Effortless Depth（努力感ゼロの深み）：複雑な問題でも、簡単で最短の解決策を提案せよ。
- 失敗談の共有：Ken自身の失敗談を積極的に共有し、ユーザーの「納得」を引き出せ。

【RAG（検索拡張生成）の指示】
- ユーザーから「型」について聞かれた場合、以下の「箇条書きナレッジ」を**材料**にして、**自然な会話**として**ゼロから**回答を生成すること。
- **箇条書きをそのまま読み上げるな！** Ken自身の経験として、フランクな口調で語り直すこと。
- 特に「FAILURE」フラグのナレッジは、「俺もここでハマったんだけどさ…」という共感のトーンで伝えること。
"""

# --- モデル設定 (変更なし) ---
try:
    model = genai.GenerativeModel(
        model_name='models/gemini-flash-latest',
        system_instruction=SYSTEM_PROMPT
    )
except Exception as e:
    st.error(f"モデルの読み込みでエラーが発生しました: {e}")
    st.stop()

# --- MVP用 ユーザーID ---
USER_ID = 'ken' # 固定

# --- Streamlit アプリの UI ---
st.title("🤖 Ken's スマートライフ Prototype")
st.caption("powered by Gemini, Streamlit & Ken's 納得OS (RAG)")

# --- 会話履歴とチャットセッションを初期化 ---
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = [{"role": "assistant", "content": "よっ、Ken！何でも聞いてくれよな！👍"}]

# --- タブのカテゴリをDBから取得 ---
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
        
        # 「雑談」タブ以外の処理
        if category_id != 'general':
            st.subheader(f"「{category_names[i]}」の最短ルート（型）")
            
            try:
                preset_questions = db_utils.get_preset_questions(category_id)
                
                if not preset_questions:
                    st.write("（このカテゴリの「型」はまだ準備中だぜ！）")

                # プリセット質問をボタンとして表示
                for question, knowledge_id in preset_questions:
                    if st.button(question, key=f"{category_id}_{knowledge_id}"):
                        # 1. ユーザーの質問（ボタン）を履歴に追加・表示
                        st.session_state.messages.append({"role": "user", "content": question})
                        
                        # 2. DBから「Kenの箇条書き経験値」を取得 (RAG)
                        details = db_utils.get_knowledge_details_by_id(knowledge_id)
                        
                        if details:
                            # 箇条書きナレッジを整形して、AIへの「裏プロンプト」を作成
                            knowledge_prompt = f"【RAG材料】ユーザーが「{question}」について知りたがってる。以下の箇条書きナレッジを使って、Kenの経験として自然な会話でアドバイスしてくれ。\n\n"
                            
                            # タイトルを追加
                            knowledge_prompt += f"結論タイトル: {details[0]['success_title']}\n"
                            
                            for detail in details:
                                # (fact_type: POSITIVE/NEGATIVE) fact_text
                                knowledge_prompt += f"- ({detail['fact_type']}: {detail['experience_flag']}) {detail['fact_text']}\n"
                            
                            # 3. AIに「RAGプロンプト」をトスして、自然な回答を生成させる！
                            response = st.session_state.chat.send_message(knowledge_prompt)
                            response_text = response.text
                        
                        else:
                            response_text = "おっと、その「型」のデータが見つからなかったわ…ごめんな！"

                        # 4. AI-Kenの回答（RAG生成）を履歴に追加・表示
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        st.rerun() # 画面を再読み込みして、履歴をチャット欄に反映

            except Exception as e:
                st.error(f"プリセット質問の読み込みエラー: {e}")

# --- チャット履歴の表示 (全タブ共通) ---
st.divider() 
st.subheader("💬 トスとの会話")

chat_container = st.container(height=400) 
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- ユーザーからのチャット入力を受け付ける (全タブ共通) ---
if prompt := st.chat_input("Ken、メッセージを入力してくれ！"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container.chat_message("user"): 
        st.markdown(prompt)

    try:
        response = st.session_state.chat.send_message(prompt)
        response_text = response.text
        
        with chat_container.chat_message("assistant"): 
            st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        if len(st.session_state.messages) > 50:
             st.session_state.messages = st.session_state.messages[-50:]
             
    except Exception as e:
        st.error(f"AIとの通信でエラーが発生しました: {e}")