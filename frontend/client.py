# 必要なライブラリをインポート
import asyncio
import boto3
import json
import uuid
import os
import streamlit as st
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

# Bedrock AgentCoreクライアントを初期化
agent_core_client = boto3.client('bedrock-agentcore')

# ページタイトルと入力欄を表示
st.title("チャットボット")
user_message = st.text_input("質問やメッセージを入力してください：")

# 非同期ストリーミング処理
async def process_stream(user_message, container):
    text_holder = container.empty()
    response = ""
    session_id = str(uuid.uuid4())
    prompt = user_message.strip()
    
    # エージェントを呼び出し
    agent_response = agent_core_client.invoke_agent_runtime(
        agentRuntimeArn=os.getenv("AGENT_RUNTIME_ARN"),
        runtimeSessionId=session_id,
        payload=json.dumps({"prompt": prompt}).encode()
    )
    
    # エージェントからのストリーミングレスポンスを処理    
    for line in agent_response["response"].iter_lines():
        if not line:
            continue
            
        line = line.decode("utf-8")
        if not line.startswith("data: "):
            continue
            
        try:
            data = json.loads(line[6:])
            
            if isinstance(data, dict):
                event = data.get("event", {})

                # ツール実行を検出して表示
                if "contentBlockStart" in event:
                    tool_use = event["contentBlockStart"].get("start", {}).get("toolUse", {})
                    tool_name = tool_use.get("name")
                    
                    # バッファをクリア
                    if response:
                        text_holder.markdown(response)
                        response = ""

                    # ツール実行のメッセージを表示
                    container.info(f"🔧 {tool_name} ツールを実行中…")
                    text_holder = container.empty()
                
                # テキストを抽出してリアルタイム表示
                elif "contentBlockDelta" in event:
                    delta = event["contentBlockDelta"]["delta"]
                    if "text" in delta:
                        text = delta["text"]
                        response += text
                        text_holder.markdown(response)
                        
        except json.JSONDecodeError:
            continue

# ボタンを押したら生成開始
if st.button("送信"):
    if user_message:
        with st.spinner("回答を生成中..."):
            container = st.container()
            asyncio.run(process_stream(user_message, container))