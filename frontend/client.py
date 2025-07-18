# 必要なライブラリをインポート
import asyncio
import boto3
import json
import codecs
import uuid
import streamlit as st

# Bedrock AgentCoreクライアントを初期化
agent_core_client = boto3.client('bedrock-agentcore')

# ページタイトルと入力欄を表示
st.title("AWSアップデート確認くん")
service_name = st.text_input("アップデートを知りたいAWSサービス名を入力してください：")

# 非同期ストリーミング処理
async def process_stream(service_name, container):
    text_holder = container.empty()
    response = ""
    session_id = str(uuid.uuid4())
    prompt = f"AWSの{service_name.strip()}の最新アップデートを、日付つきで要約して。"
    
    # エージェントを呼び出し
    agent_response = agent_core_client.invoke_agent_runtime(
        agentRuntimeArn="arn:aws:bedrock-agentcore:us-west-2:715841358122:runtime/main-vsNCwb7avp",
        runtimeSessionId=session_id,
        payload=json.dumps({"prompt": prompt}).encode()
    )
    
    # ストリーミングレスポンスを処理
    for line in agent_response["response"].iter_lines(chunk_size=10):
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                line = line[6:]
                try:
                    # JSONデータをパース
                    data = json.loads(line)
                    
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
                        
                        # contentBlockDeltaイベントからテキストを抽出
                        elif "contentBlockDelta" in event:
                            delta = event["contentBlockDelta"]["delta"]
                            if "text" in delta:
                                text = delta["text"]
                                # Unicodeエスケープをデコード
                                try:
                                    decoded_text = codecs.decode(text, 'unicode_escape').encode('latin1').decode('utf-8')
                                    response += decoded_text
                                    text_holder.markdown(response)
                                except:
                                    response += text
                                    text_holder.markdown(response)
                        
                        # テキストを抽出してリアルタイム表示（dataフィールドから）
                        elif text := data.get("data"):
                            response += text
                            text_holder.markdown(response)
                                    
                except json.JSONDecodeError:
                    # JSONでない場合はスキップ
                    pass

# ボタンを押したら生成開始
if st.button("確認"):
    if service_name:
        with st.spinner("アップデートを確認中..."):
            container = st.container()
            asyncio.run(process_stream(service_name, container))
