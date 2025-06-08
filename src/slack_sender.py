"""
Slackへのメッセージ送信を扱うモジュール
"""
import os
from slack_sdk.webhook import WebhookClient
from slack_sdk.errors import SlackApiError
from .config_loader import get_config
from .utils import print_with_timestamp

def send_to_slack(message):
    config = get_config()
    webhook_env_var = config.get('slack', {}).get('webhook_url_env', 'SLACK_WEBHOOKS')
    test_mode = config.get('slack', {}).get('test_mode', False)
    
    # 環境変数のデバッグ情報を表示
    print_with_timestamp(f"Slack webhook環境変数名: {webhook_env_var}")
    print_with_timestamp(f"テストモード: {test_mode}")
    
    # 利用可能な環境変数の一部をチェック (セキュリティのため完全な値は表示しない)
    for env_var in ['SLACK_WEBHOOKS', 'GEMINI_API_KEY', 'GITHUB_WORKFLOW']:
        if os.environ.get(env_var):
            masked_value = os.environ.get(env_var)[:5] + '...' if os.environ.get(env_var) else 'なし'
            print_with_timestamp(f"環境変数 {env_var} が設定されています: {masked_value}")
        else:
            print_with_timestamp(f"環境変数 {env_var} は設定されていません")
    
    webhook_url = os.environ.get(webhook_env_var)
    
    try:
        if not webhook_url:
            print_with_timestamp(f"Slack webhook URLが環境変数 {webhook_env_var} に設定されていません。GitHubリポジトリのSecretsを確認してください。")
            return None
        
        # テストモードの場合は実際に送信せず、メッセージを表示するのみ
        if test_mode:
            print_with_timestamp("テストモードが有効なため、Slackへの実際の送信をスキップします。")
            print_with_timestamp("送信予定のメッセージ内容:")
            if "blocks" in message:
                for block in message["blocks"]:
                    if block.get("type") == "section" and "text" in block:
                        text_content = block["text"].get("text", "")
                        print_with_timestamp(f"- {text_content[:100]}..." if len(text_content) > 100 else f"- {text_content}")
            return None
            
        webhook = WebhookClient(webhook_url)
        response = webhook.send(**message)
        print_with_timestamp(f"Slackへの送信が完了しました。ステータスコード: {response.status_code}")
        return response
    except SlackApiError as e:
        print_with_timestamp(f"Slackへの送信中にAPIエラーが発生しました: {e}")
        return None
    except Exception as e:
        print_with_timestamp(f"Slackへの送信中に予期しないエラーが発生しました: {e}")
        return None
        
def add_greeting_to_message(message):
    """メッセージにあいさつを追加する"""
    if message and "blocks" in message:
        message["blocks"].insert(0, {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*おはよう☀️ 論文を紹介するので一読してね*"
            }
        })
    return message
