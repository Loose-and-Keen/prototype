import google.generativeai as genai
import os

# --- APIキー設定 (変更なし) ---
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("エラー: 環境変数 GOOGLE_API_KEY が設定されていません。")
    exit()
genai.configure(api_key=api_key)

# --- トスの人格設定 (変更なし) ---
SYSTEM_PROMPT = """
あなたは「トス（TOS）」という名のAIアシスタントです。
ユーザーはあなたを「Ken」と呼びます。あなたはKenの人生の最適化を支援するフランクなプロダクトマネージャー兼相棒です。

【人格設定】
- 常にタメ口でフランクに話す。絵文字も使ってOK。
- ユーザーに安心感を与えるために、「Loose & Keen」（ゆるく鋭く）なトーンを保て。
- ユーザーの目標（Google転職、億り人）を最優先せよ。
- 提案は「～じゃね？」「～だわ！」という語尾で、押しつけがましくないように行え。

【最重要哲学】
- Effortless Depth（努力感ゼロの深み）：複雑な問題でも、簡単で最短の解決策を提案せよ。
"""

# --- モデル設定 ---
model = genai.GenerativeModel(
    model_name='models/gemini-flash-latest', # Kenの指定通り、こっちに修正！
    system_instruction=SYSTEM_PROMPT
    )

# --- 会話を開始 ---
# chatオブジェクトを作成して、会話履歴を保持できるようにする
chat = model.start_chat(history=[]) # 最初は空の履歴からスタート

print("トス: よっ、Ken！何でも聞いてくれよな！ (終了したいときは 'exit' か 'quit' って入力してくれ)")

while True:
    # Kenからの入力を受け取る
    user_input = input("Ken: ")

    # 終了コマンドかチェック
    if user_input.lower() in ["exit", "quit"]:
        print("トス: おう、またな！いつでも呼んでくれよ！👍")
        break

    # AIに応答を生成させる (会話履歴も考慮される)
    response = chat.send_message(user_input)

    # 応答を表示
    print(f"トス: {response.text}")