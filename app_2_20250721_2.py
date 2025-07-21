import streamlit as st
import time
from datetime import datetime, timedelta
import pytz
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from streamlit_autorefresh import st_autorefresh

# セッション初期化
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "response_ready_time" not in st.session_state:
    st.session_state.response_ready_time = None
if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""
if "selected_tz" not in st.session_state:
    st.session_state.selected_tz = "Asia/Tokyo"

# 自動リフレッシュ：30秒ごと
st_autorefresh(interval=30 * 1000, key="autorefresh")

# 世界のタイムゾーン選択
st.sidebar.subheader("🌍 タイムゾーンを選択")
timezone_options = {
    "🇯🇵 日本 (JST)": "Asia/Tokyo",
    "🇺🇸 アメリカ西海岸 (PST)": "America/Los_Angeles",
    "🇺🇸 アメリカ東海岸 (EST)": "America/New_York",
    "🇬🇧 イギリス (GMT)": "Europe/London",
    "🇸🇬 シンガポール": "Asia/Singapore",
    "🌐 UTC": "UTC"
}
tz_display = st.sidebar.selectbox("表示用タイムゾーン", list(timezone_options.keys()))
selected_tz = timezone_options[tz_display]
st.session_state.selected_tz = selected_tz

# タイトル
st.title("🧠 Think with Me：問いかけ型AI")

# APIキー入力
api_key_input = st.text_input("🔑 OpenAI API Key", type="password")
if api_key_input:
    st.session_state.api_key = api_key_input

# ユーザー入力欄
st.subheader("💬 今考えたいテーマは？")
user_input = st.text_area("あなたが考えたいこと")

# 考える時間（10分〜60分）
st.subheader("⏳ 考える時間を選んでください")
wait_minutes = st.selectbox("考える時間（分）", [3, 10, 20, 30, 40, 50, 60])

# 実行ボタン
if st.button("🧠 思考をスタートする"):
    if not user_input:
        st.warning("まずテーマを入力してください。")
    elif not st.session_state.api_key:
        st.warning("OpenAI APIキーを入力してください。")
    else:
        # 現在時刻（UTC）と選択タイムゾーン変換
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
        user_tz = pytz.timezone(selected_tz)
        response_ready_utc = now_utc + timedelta(minutes=wait_minutes)
        st.session_state.response_ready_time = response_ready_utc
        st.session_state.last_user_input = user_input
        st.session_state.messages = [HumanMessage(content=user_input)]

        # 表示用時刻（選択タイムゾーンに変換）
        response_local_time = response_ready_utc.astimezone(user_tz)
        formatted_time = response_local_time.strftime("%Y-%m-%d %H:%M")

        st.success(f"✅ {wait_minutes}分の考える時間を開始しました。")
        st.info(f"⏳ **{formatted_time}（{tz_display}）以降にこのページを開くと、AIが問いかけを返します。**")

# AI応答（時間が過ぎていれば）
now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
if st.session_state.response_ready_time and now_utc >= st.session_state.response_ready_time:
    if not any(isinstance(msg, AIMessage) for msg in st.session_state.messages):
        st.info("⌛ 考える時間が終了しました。AIが問いかけを返します...")

        llm = ChatOpenAI(
            openai_api_key=st.session_state.api_key,
            model="gpt-4",
            temperature=0.7
        )

        system_prompt = (
            "あなたはユーザーの思考を促すコーチです。"
            "ユーザーが深く考えるための質問を、1つか2つ、丁寧に返してください。"
            "決して即答や解決を急がないでください。"
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=st.session_state.last_user_input)
        ]

        response = llm(messages)
        st.session_state.messages.append(AIMessage(content=response.content))

# チャット履歴表示
if st.session_state.messages:
    st.subheader("📝 対話ログ")
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            st.markdown(f"🧑‍💬 **あなた**: {msg.content}")
        elif isinstance(msg, AIMessage):
            st.markdown(f"🤖 **AI**: {msg.content}")
