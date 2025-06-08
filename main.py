from src.utils import print_with_timestamp
from src.config_loader import load_config, get_config
from src.arxiv_client import get_random_paper
from src.gemini_processor import process_paper_with_gemini
from src.paper_formatter import format_paper_for_slack
from src.slack_sender import send_to_slack, add_greeting_to_message

def main():
    load_config()
    print_with_timestamp("ArXiv to Slack 処理を開始します")
    paper = get_random_paper()
    config = get_config()
    use_gemini = config.get('gemini', {}).get('use_gemini', False)
    if use_gemini:
        paper = process_paper_with_gemini(paper)
    message = format_paper_for_slack(paper)
    message = add_greeting_to_message(message)
    send_to_slack(message)

if __name__ == "__main__":
    main()
