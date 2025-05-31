"""
Slackへのメッセージ送信を扱うモジュール
"""
import os
from slack_sdk.webhook import WebhookClient
from slack_sdk.errors import SlackApiError
from .config_loader import get_config
from .utils import print_with_timestamp

def send_to_slack(message):
    """Slackにメッセージを送信する"""
    config = get_config()
    
    # 環境変数名を設定ファイルから取得
    webhook_env_var = config.get('slack', {}).get('webhook_url_env', 'SLACK_WEBHOOK_URL')
    
    # 環境変数からWebhook URLを取得
    webhook_url = os.environ.get(webhook_env_var)
    
    try:
        # URLが設定されているか確認
        if not webhook_url:
            print_with_timestamp(f"Slack webhook URLが環境変数 {webhook_env_var} に設定されていません。.envファイルを確認してください。")
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
                "text": "おはよう☀️ 今日の論文はこちら!!"
            }
        })
    return message
