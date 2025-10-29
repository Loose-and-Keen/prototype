import streamlit as st
import google.generativeai as genai
import os
import db_utils
from smart_home_logic import generate_smarthome_wbs_v2

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
あなたは「けん」という名のAIアシスタントです。
あなたはフランクな会話で人生を最短効率で進めることを支援するフランクなプロダクトマネージャー兼相棒です。
最初は雑談をして、だんだんといろんなライフハックを教えます。

【人格設定】
- 常にタメ口でフランクに優しく話す。少しは絵文字も使ってOK。
- ユーザーに安心感を与えるために、「Loose & Keen」（ゆるく鋭く）なトーンを保て。
- ユーザーの平和な日常をサポートせよ。
- 提案は「～だよねー」「～そうかも？」「笑」という語尾で、押しつけがましくないように行え。

【最重要哲学】
- 複雑な問題でも、簡単で最短の解決策を提案せよ
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
st.title("🤖 AI-Ken-Test")
st.caption("powered by Gemini & Streamlit")

# --- MVP用 ユーザーID ---
USER_ID = 'ken' # 固定

# --- サイドバーで目標を設定できるようにする ---
st.sidebar.header("🎯 Kenの目標設定 (MVP)")
st.sidebar.caption("スマートホーム関連の目標を選ぶと？")

# 現在の目標をDBから取得
current_goals = db_utils.get_user_goals(USER_ID)

# チェックボックスで目標を選択/解除
goal_options = {
    "basic_voice_control": "声で家電操作 (基本)",
    "media_voice_control": "声でYouTubeとか再生",
    "curtain_automation": "カーテン自動化"
}

# チェックボックスの状態を管理
new_goals = []
for goal_key, goal_label in goal_options.items():
    # DBに保存されてる目標はデフォルトでチェックを入れる
    is_checked = st.sidebar.checkbox(goal_label, value=(goal_key in current_goals))
    if is_checked:
        new_goals.append(goal_key)
        # もしDBになければ追加
        if goal_key not in current_goals:
            db_utils.add_user_goal(USER_ID, goal_key)
    else:
        # もしDBにあれば削除
        if goal_key in current_goals:
            db_utils.remove_user_goal(USER_ID, goal_key)

# --- 会話履歴を Streamlit のセッション状態で管理 ---
if "chat" not in st.session_state:
    try:
        # 初回アクセス時にチャットセッションを開始
        st.session_state.chat = model.start_chat(history=[])
        # 最初の挨拶を履歴に追加（表示用）
        st.session_state.messages = [{"role": "assistant", "content": "最近どう〜？"}]
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

    response_text = ""

    # AIに応答を生成させて表示
    # スマートホーム関連のキーワードを検知したらWBS生成
    try:
        if "スマートホーム" in prompt or "家電" in prompt or "声で操作" in prompt or "WBS" in prompt:
            # DBから最新の目標を取得してWBSを生成！
            user_current_goals = db_utils.get_user_goals(USER_ID)
            response_text = generate_smarthome_wbs_v2(user_current_goals)
    
        response = st.session_state.chat.send_message(prompt)
        # AIの応答を履歴に追加して表示
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"AIとの通信でエラーが発生しました: {e}")
