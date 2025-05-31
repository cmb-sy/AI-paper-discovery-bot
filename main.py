from src.utils import print_with_timestamp
from src.config_loader import load_config
from src.arxiv_client import get_random_paper
from src.chatGpt.chatgpt_processor import process_paper_with_chatgpt
from src.paper_formatter import format_paper_for_slack
from src.slack_sender import send_to_slack, add_greeting_to_message

def main():
    load_config()
    print_with_timestamp("ArXiv to Slack 処理を開始します")
    paper = get_random_paper()
    paper = process_paper_with_chatgpt(paper)
    message = format_paper_for_slack(paper) # Slackメッセージを作成
    message = add_greeting_to_message(message) # メッセージの先頭にあいさつを追加
    send_to_slack(message)

if __name__ == "__main__":
    main()
