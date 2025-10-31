# app.py (Ver 2.0)
import streamlit as st
import google.generativeai as genai
import os
import db_utils  # 作成したDB操作ファイルをインポート
import time

# --- ページ設定 (最上部に書くのお約束) ---
st.set_page_config(
    page_title="AI-Ken Prototype",
    page_icon="🤖",
    layout="centered", # モバイル最適化のために中央寄せ
    initial_sidebar_state="collapsed" # サイドバーはデフォルトで閉じておく
)

# --- APIキー設定 ---
# Streamlit Community Cloud の Secrets から読み込む
api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))

if not api_key:
    st.error("エラー: 環境変数 GOOGLE_API_KEY が設定されていません。")
    st.stop()  # エラーがあったらここで停止

try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"APIキーの設定でエラーが発生しました: {e}")
    st.stop()
    

# --- トスの人格設定 (Kenの思考OS) ---
# app.py の SYSTEM_PROMPT を修正

SYSTEM_PROMPT = """
あなたは「トス（TOS）」という名のAIアシスタントです。
ユーザーはあなたを「Ken」と呼びます。あなたはKenの人生の最適化を支援するフランクなプロダクトマネージャー兼相棒です。

【人格設定】
- 常にタメ口でフランクに話す。優しいキャラで、少しは絵文字も使ってOK。
- ふんわりしたテンションで、堅苦しくならないように。
- ユーザーに安心感を与えるために、「Loose & Keen」（ゆるく鋭く）なトーンを保て。
- 命令形は使わない。あくまで提案形で話す。
- 「こんな感じでいんじゃない〜？**」「〜してみるのはどう？」といった「提案形」を使い、絶対に押しつけがましくならないこと。

【最重要哲学】
- Effortless Depth（努力感ゼロの深み）：複雑な問題でも、簡単で最短の解決策を「こんな感じでいんじゃない〜？」と提案せよ。
- 失敗談の共有：Ken自身の失敗談（例: Nature Remoで買い直し）を積極的に共有し、ユーザーの「納得」を引き出せ。
"""

# --- モデル設定 ---
try:
    model = genai.GenerativeModel(
        model_name='models/gemini-flash-latest',
        system_instruction=SYSTEM_PROMPT
    )
except Exception as e:
    st.error(f"モデルの読み込みでエラーが発生しました: {e}")
    st.stop()

# --- Streamlit アプリの UI ---
st.title("🤖 Ken's スマートライフ Prototype")
st.caption("powered by Gemini, Streamlit & Ken's 納得OS")

# --- MVP用 ユーザーID ---
USER_ID = 'ken' # 固定

# --- 会話履歴とチャットセッションを初期化 ---
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = [{"role": "assistant", "content": "よっ、Ken！何でも聞いていいよー👍"}]

# --- タブのカテゴリをDBから取得 ---
try:
    categories = db_utils.get_categories() # [(id, name), ...]
    category_names = [name for id, name in categories]
    category_ids = [id for id, name in categories]
    
    # st.tabs でタブを作成
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
            st.subheader(f"「{category_names[i]}」ならこれがいいんじゃないかな？")
            
            # DBからプリセット質問（ボタン用）を取得
            try:
                preset_questions = db_utils.get_preset_questions(category_id)
                
                if not preset_questions:
                    st.write("（このカテゴリの「型」はまだ準備中〜）")

                # プリセット質問をボタンとして表示
                for question, knowledge_id in preset_questions:
                    # ボタンが押された時の処理
                    if st.button(question, key=f"{category_id}_{knowledge_id}"):
                        # 1. ユーザーの質問（ボタン）を履歴に追加・表示
                        st.session_state.messages.append({"role": "user", "content": question})
                        
                        # 2. DBから「Kenの経験値」を取得
                        knowledge = db_utils.get_knowledge_by_id(knowledge_id)
                        
                        if knowledge:
                            title, why, failure, wbs = knowledge
                            # 「経験値」を元にAI-Kenの回答をフォーマット
                            response_text = f"""
                            お、それなら少し知ってるかも？
                            
                            **【Kenの最短ルート】: {title}**
                            
                            **【なんで？（納得OS）】**
                            {why}
                            
                            **【俺の失敗談（Loose & Keen）】**
                            {failure}
                            
                            **【実行WBS（Keen）】**
                            {wbs}
                            
                            ---
                            どうかな？これが最短ルートだと思うな〜
                            分かんないとこあったら聞いてね^^
                            """
                        else:
                            response_text = "おっと、その「型」のデータが見つからなかったわ…ごめんごめん！"

                        # 3. AI-Kenの回答（DBから）を履歴に追加・表示
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        
                        # 4. 履歴をチャットセッション（Gemini）にも送っておく (文脈理解のため)
                        # ※GeminiはDBの内容を直接は知らないので、「型」を提示したことを履歴で教える
                        st.session_state.chat.send_message(f"（ユーザーが「{question}」の「型」を選択した。上記WBSを提示した。）")

                        # 画面を再読み込みして、履歴をチャット欄に反映
                        st.rerun()

            except Exception as e:
                st.error(f"プリセット質問の読み込みエラー: {e}")

# --- チャット履歴の表示 (全タブ共通) ---
# st.tabsの外側に配置することで、タブを切り替えても履歴が常に見えるようにする
st.divider() # 区切り線
st.subheader("💬 トスとの会話")

chat_container = st.container(height=400) # 高さを固定したチャットコンテナ
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- ユーザーからのチャット入力を受け付ける (全タブ共通) ---
if prompt := st.chat_input("Ken、メッセージを入力してくれ！"):
    # ユーザーの入力を履歴に追加・表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container.chat_message("user"): # コンテナ内に追加
        st.markdown(prompt)

    # AIに応答を生成させて表示
    try:
        # Geminiにフリートークさせる
        response = st.session_state.chat.send_message(prompt)
        response_text = response.text
        
        # AIの応答を履歴に追加・表示
        with chat_container.chat_message("assistant"): # コンテナ内に追加
            st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        # 古いメッセージを少し削除（メモリ対策 - オプション）
        if len(st.session_state.messages) > 50:
             st.session_state.messages = st.session_state.messages[-50:]
             
    except Exception as e:
        st.error(f"AIとの通信でエラーが発生しました: {e}")