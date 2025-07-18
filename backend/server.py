from strands import Agent, tool
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import feedparser

# ツールを定義
@tool
def get_aws_updates(service_name: str) -> str:
    # AWS What's NewのRSSフィードをパース
    feed = feedparser.parse("https://aws.amazon.com/about-aws/whats-new/recent/feed/")    
    result = []

    # フィードの各エントリをチェック
    for entry in feed.entries:
        # 件名にサービス名が含まれているかチェック
        if service_name.lower() in entry.title.lower():
            result.append({
                "published": entry.get("published", "N/A"),
                "summary": entry.get("summary", "")
            })
            
            # 最大3件のエントリを取得
            if len(result) >= 3:
                break

    return result

app = BedrockAgentCoreApp()
bedrock_model = BedrockModel(
    region_name="us-west-2",
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
)
agent = Agent(
    model=bedrock_model,
    system_prompt="日本語で話してね。",
    tools=[get_aws_updates]
)

@app.entrypoint
async def invoke(payload):
    """ユーザーの質問にストリーミングで答えてください。"""
    user_message = payload.get("prompt", "こんにちは！")
    
    # ストリーミングでレスポンスを生成
    stream = agent.stream_async(user_message)
    async for event in stream:
        print(event)  # デバッグ用
        yield event

app.run()
