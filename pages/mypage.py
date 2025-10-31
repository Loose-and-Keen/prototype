# pages/mypage.py

import streamlit as st
import db_utils # DB操作ファイルをインポート

# --- MVP用 ユーザーID ---
USER_ID = 'ken' # 固定

st.set_page_config(
    page_title="Ken's マイページ",
    page_icon="😎"
)

st.title(f"😎 Kenのマイページ")
st.caption("人生RPGの進捗だぜ！")

# --- DBから「型」のカテゴリを取得 ---
try:
    categories = db_utils.get_categories()
    
    for category_id, category_name in categories:
        if category_id == 'general': # 雑談は除く
            continue
        
        st.subheader(f"{category_name} の「型」")
        
        # DBからそのカテゴリの目標（WBSタスク）を取得
        user_goals = db_utils.get_user_goals_by_category(USER_ID, category_id) # ← これ新しい関数だから後でDB Utilsに追加するぜ！
        
        if not user_goals:
            st.write("（このカテゴリのクエストはまだ受けてないぜ！）")
        else:
            for goal_key, status in user_goals:
                # DBから取得したステータスでチェックボックスの初期状態を決める
                is_completed = (status == 'completed')
                
                # チェックボックスでタスクの完了/未完了を管理
                if st.checkbox(f"【{goal_key}】を達成！", value=is_completed, key=f"{USER_ID}_{goal_key}"):
                    # チェックが入ったらDBを 'completed' に更新
                    if not is_completed:
                        db_utils.update_user_goal_status(USER_ID, goal_key, 'completed') # ←これも新しい関数
                        st.balloons() # 達成おめでとう！
                else:
                    # チェックが外れたらDBを 'not_started' に戻す
                    if is_completed:
                        db_utils.update_user_goal_status(USER_ID, goal_key, 'not_started') # ←これも新しい関数

except Exception as e:
    st.error(f"マイページの読み込みでエラーが発生しました: {e}")