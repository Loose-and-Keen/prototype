# smart_home_logic.py

# --- Kenのおすすめデバイス (定数化しとくと楽) ---
RECOMMENDED_HUB = "SwitchBot Hub Mini (中古)"
RECOMMENDED_VOICE_ASSISTANT = "Amazon Echo Show (中古)"
RECOMMENDED_STREAMING = "Amazon Fire TV Stick (中古)"
RECOMMENDED_CURTAIN = "SwitchBot カーテン" # これは新品推奨かも
AVOID_HUB_NOTE = "※Nature Remo Miniも人気だけど、カーテン自動化とか将来の拡張性を考えるとSwitchBotが断然おすすめだぜ！"

def generate_smarthome_wbs_v2(user_goals=["basic_voice_control"]):
    """
    ユーザーの目標に基づいてスマートホーム化のWBSを生成する (V2: Kenの経験ベース)
    user_goals: "basic_voice_control", "media_voice_control", "curtain_automation" などをリストで受け取る想定
    """

    wbs = "よっしゃ、Kenの経験に基づいた「イージーライフ」実現への最短ルートWBSだ！😎\n\n"
    total_budget_estimate_min = 0 # 概算予算（最低）
    phases_included = [] # 実行するフェーズ

    # --- フェーズ分け ---

    # フェーズ1: 声の相棒 (音楽・タイマー・ニュース) - 全ての基本
    if any(goal in user_goals for goal in ["basic_voice_control", "media_voice_control", "curtain_automation"]):
        phases_included.append(1)
        wbs += f"**フェーズ1: まずは声の相棒を手に入れろ！ (予算目安: 〜3000円)**\n"
        wbs += f"1. **【調査＆購入】メルカリで「{RECOMMENDED_VOICE_ASSISTANT}」を探してゲット！** キッチンタイマーとか『おはよう』でニュース・天気予報流すだけでも生活変わるぜ。\n"
        wbs += f"   * これで音楽・ニュース・タイマーの基本自動化はOK。\n\n"
        total_budget_estimate_min += 2000 # 中古相場

    # フェーズ2: 家電リモコン操作 (エアコン・テレビ・照明)
    if any(goal in user_goals for goal in ["basic_voice_control", "curtain_automation"]): # カーテンやるならハブは必須
        phases_included.append(2)
        wbs += f"**フェーズ2: 家中の赤外線リモコンを声でハック！ (予算目安: 〜3000円)**\n"
        wbs += f"2. **【調査＆購入】メルカリで「{RECOMMENDED_HUB}」を探してゲット！** こいつが赤外線リモコンの親玉になる。\n"
        wbs += f"   * {AVOID_HUB_NOTE}\n" # ← Kenの最重要知見！
        wbs += f"3. **【設定】SwitchBotアプリでWi-Fi接続して、テレビ・エアコン・照明のリモコンを登録！** アプリの指示通りやれば余裕だぜ。\n"
        wbs += f"4. **【連携】Alexaアプリ（フェーズ1で入れたやつ）でSwitchBotスキルを有効化！** これで「アレクサ、テレビつけて」が可能になる。\n\n"
        total_budget_estimate_min += 2000 # 中古相場

    # フェーズ3: メディア操作 (YouTubeなど)
    if "media_voice_control" in user_goals:
        phases_included.append(3)
        wbs += f"**フェーズ3: YouTubeも声で再生！ (予算目安: 〜3000円)**\n"
        wbs += f"5. **【調査＆購入】メルカリで「{RECOMMENDED_STREAMING}」を探してゲット！** これをテレビに挿すんだ。\n"
        wbs += f"6. **【設定＆連携】Fire TV Stickをセットアップして、Alexaと連携！** 「アレクサ、YouTubeで〇〇流して」が実現する。\n\n"
        total_budget_estimate_min += 2000 # 中古相場

    # フェーズ4: カーテン自動化
    if "curtain_automation" in user_goals:
        if 2 not in phases_included: # ハブがないと動かない
             wbs += f"**【注意！】カーテン自動化には「{RECOMMENDED_HUB}」が必須だぜ！フェーズ2からやるのがおすすめだ。\n\n"
        else:
            phases_included.append(4)
            wbs += f"**フェーズ4: カーテンも自動で開け閉め！ (予算目安: 〜7000円/枚)**\n"
            wbs += f"7. **【購入】「{RECOMMENDED_CURTAIN}」をゲット！** カーテンレールに合わせてタイプ（U型/角型）を選ぶんだぜ。\n"
            wbs += f"8. **【設定】SwitchBotアプリでカーテンデバイスを追加して、{RECOMMENDED_HUB}と連携！**\n"
            wbs += f"9. **【自動化】アプリで「シーン」を作成！** 「朝7時にカーテン開ける」とか「アレクサ、カーテン閉めて」とか設定できる。\n\n"
            total_budget_estimate_min += 6000 # 新品相場

    # --- まとめ ---
    if not phases_included:
        wbs = "おっと、具体的な目標がまだ決まってないみたいだな？ まずは「声で電気つけたい」とか「カーテン自動化したい」とか、やりたいことを教えてくれよな！"
    else:
        wbs += f"**---\nこれで大体OKだ！選んだフェーズ全部やっても、総額目安は【約{total_budget_estimate_min}円〜】くらいかな。どうよ、Ken？これなら具体的なイメージ湧くだろ？👍**"

    return wbs

# --- テスト用 ---
if __name__ == '__main__':
    print("--- 基本プラン (声で家電操作) ---")
    print(generate_smarthome_wbs_v2(["basic_voice_control"]))
    print("\n--- フルプラン (全部入り) ---")
    print(generate_smarthome_wbs_v2(["basic_voice_control", "media_voice_control", "curtain_automation"]))
    print("\n--- カーテンだけやりたい場合 (ハブが必要な旨が表示される) ---")
    print(generate_smarthome_wbs_v2(["curtain_automation"]))