# Bedrock AgentCore サンプル

## 構築手順

### ECRプライベートリポジトリ作成

```sh
aws ecr create-repository --repository-name <好きな名前>
```

### IAMポリシー作成

```sh
# ロールと信頼ポリシーを作成
aws iam create-role \
    --role-name BedrockAgentCoreExecutionRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock-agentcore.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }'

# 必要なポリシーをアタッチ
aws iam attach-role-policy --role-name BedrockAgentCoreExecutionRole --policy-arn
arn:aws:iam::aws:policy/BedrockAgentCoreFullAccess
aws iam attach-role-policy --role-name BedrockAgentCoreExecutionRole --policy-arn
arn:aws:iam::aws:policy/AmazonBedrockFullAccess
aws iam attach-role-policy --role-name BedrockAgentCoreExecutionRole --policy-arn
arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
aws iam attach-role-policy --role-name BedrockAgentCoreExecutionRole --policy-arn
arn:aws:iam::aws:policy/CloudWatchFullAccessV2
aws iam attach-role-policy --role-name BedrockAgentCoreExecutionRole --policy-arn
arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess
```

### AgentCoreにデプロイ

```sh
agentcore configure --entrypoint backend/server.py -er <IAMロールのARN>
agentcore launch
```

### クライアントを起動

```sh
streamlit run client/gui.py
```