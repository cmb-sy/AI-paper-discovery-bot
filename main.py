#!/usr/bin/env python3
"""
ArXiv論文取得・処理・Slack通知の実行スクリプト
"""
import sys
from src.utils import print_with_timestamp
from src.config_loader import load_config
from src.arxiv_client import get_random_paper
from src.chatGpt.chatgpt_processor import process_paper_with_chatgpt
from src.paper_formatter import format_paper_for_slack
from src.slack_sender import send_to_slack, add_greeting_to_message

def main():
    """メイン実行関数"""
    # 設定を読み込む
    load_config()
    
    print_with_timestamp("ArXiv to Slack 処理を開始します")
    
    # 論文を取得
    paper = get_random_paper()
    
    if not paper:
        return
    
    # ChatGPTでの処理（設定に基づく）
    paper = process_paper_with_chatgpt(paper)
    
    # Slackメッセージを作成
    message = format_paper_for_slack(paper)
    
    # メッセージにあいさつを追加
    message = add_greeting_to_message(message)
    
    # Slackに送信
    send_to_slack(message)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_with_timestamp("ユーザーによって処理が中断されました")
        sys.exit(0)
    except Exception as e:
        print_with_timestamp(f"予期しないエラーが発生しました: {e}")
        sys.exit(1)
