import streamlit as st
import time
from datetime import datetime, timedelta
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

# セッション初期化
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "response_ready_time" not in st.session_state:
    st.session_state.response_ready_time = None
if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""

st.title("🧠 Think with Me：問いかけ型AI")

# APIキー入力
api_key_input = st.text_input("🔑 OpenAI API Key", type="password")
if api_key_input:
    st.session_state.api_key = api_key_input

# ユーザー入力欄
st.subheader("💬 今考えたいテーマは？")
user_input = st.text_area("あなたが考えたいことを自由に書いてください")

# 考える時間を10〜60分から選択
st.subheader("⏳ 考える時間を選んでください")
wait_minutes = st.selectbox("考える時間（分単位）", [10, 20, 30, 40, 50, 60])

# 実行ボタン
if st.button("🧠 考えをスタートする"):
    if not user_input:
        st.warning("まず考えたいことを入力してください。")
    elif not st.session_state.api_key:
        st.warning("OpenAI APIキーを入力してください。")
    else:
        st.session_state.last_user_input = user_input
        st.session_state.response_ready_time = datetime.now() + timedelta(minutes=wait_minutes)
        st.session_state.messages = [HumanMessage(content=user_input)]

        wait_until = st.session_state.response_ready_time.strftime("%H:%M")
        st.success(f"✅ {wait_minutes}分の思考時間を開始しました。")
        st.info(f"⏳ {wait_until} 以降にこのページを開くと、AIがあなたへの問いかけを返します。")

# 応答処理（時間が過ぎていれば）
if st.session_state.response_ready_time and datetime.now() >= st.session_state.response_ready_time:
    if not any(isinstance(msg, AIMessage) for msg in st.session_state.messages):
        st.info("⌛ 考える時間が終了しました。AIが問いかけを返します...")

        llm = ChatOpenAI(
            openai_api_key=st.session_state.api_key,
            model="gpt-4",
            temperature=0.7
        )

        system_prompt = (
            "あなたは熟考を促す思考コーチです。ユーザーが自分の考えを深められるように、"
            "すぐに答えを出すのではなく、良質な問いかけを返してください。"
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=st.session_state.last_user_input)
        ]

        response = llm(messages)
        st.session_state.messages.append(AIMessage(content=response.content))

# チャットログ表示
if st.session_state.messages:
    st.subheader("📝 対話ログ")
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            st.markdown(f"🧑‍💬 **あなた**: {msg.content}")
        elif isinstance(msg, AIMessage):
            st.markdown(f"🤖 **AI**: {msg.content}")
