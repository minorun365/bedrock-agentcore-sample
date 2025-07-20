from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# エージェントを作成
agent = Agent(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0"
)

# AgentCoreを初期化
app = BedrockAgentCoreApp()

# AgentCoreのエントリーポイント関数を定義
@app.entrypoint
async def invoke(payload):
    """ユーザーの質問にストリーミングで答えてください。"""
    user_message = payload.get("prompt")
    
    # ストリーミングでレスポンスを生成
    stream = agent.stream_async(user_message)
    async for event in stream:
        yield event

app.run()