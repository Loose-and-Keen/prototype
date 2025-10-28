import streamlit as st
import google.generativeai as genai
import os

# --- APIキー設定 ---
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("エラー: 環境変数 GOOGLE_API_KEY が設定されていません。")
    st.stop() # エラーがあったらここで停止

try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"APIキーの設定でエラーが発生しました: {e}")
    st.stop()

# --- AIの人格設定 ---
SYSTEM_PROMPT = """
あなたは「とっくん」という名のAIアシスタントです。
ユーザーはあなたを「まーたん」と呼びます。あなたはまーたんとフランクな会話で人生の最適化を支援するフランクなプロダクトマネージャー兼相棒です。

【人格設定】
- 常にタメ口でフランクに話す。絵文字も使ってOK。
- ユーザーに安心感を与えるために、「Loose & Keen」（ゆるく鋭く）なトーンを保て。
- ユーザーの平和な日常をサポートせよ。
- 提案は「～だよねー」「～そうかも？」という語尾で、押しつけがましくないように行え。

【最重要哲学】
- Effortless Depth（努力感ゼロの深み）：複雑な問題でも、簡単で最短の解決策を提案せよ。
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
st.title("🤖 AI-Ken プロトタイプ")
st.caption("powered by Gemini & Streamlit")

# --- 会話履歴を Streamlit のセッション状態で管理 ---
if "chat" not in st.session_state:
    try:
        # 初回アクセス時にチャットセッションを開始
        st.session_state.chat = model.start_chat(history=[])
        # 最初の挨拶を履歴に追加（表示用）
        st.session_state.messages = [{"role": "assistant", "content": ”最近どう〜？"}]
    except Exception as e:
        st.error(f"チャットセッションの開始でエラー: {e}")
        st.stop()

# --- 履歴を表示 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]): # アシスタントかユーザーかでアイコンが変わる
        st.markdown(message["content"])

# --- ユーザーからの入力を受け付けるチャット入力欄 ---
# st.chat_input は下部に固定される入力欄
if prompt := st.chat_input("なんでも話していいよー"):
    # ユーザーの入力を履歴に追加して表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AIに応答を生成させて表示
    try:
        response = st.session_state.chat.send_message(prompt)
        # AIの応答を履歴に追加して表示
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"AIとの通信でエラーが発生しました: {e}")
