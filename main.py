from src.utils import print_with_timestamp
from src.config_loader import load_config, get_config
from src.arxiv_client import get_random_paper
from src.gemini_processor import process_paper_with_gemini
from src.chatgpt_processor import process_paper_with_chatgpt
from src.paper_formatter import format_paper_for_slack
from src.slack_sender import send_to_slack, add_greeting_to_message

def main():
    """メイン処理関数"""
    try:
        load_config()
        print_with_timestamp("ArXiv to Slack 処理を開始します")
        
        # 論文の取得
        paper = get_random_paper()
        if not paper:
            print_with_timestamp("論文の取得に失敗しました。処理を終了します。")
            return
        
        config = get_config()
        llm_provider = config.get('llm', {}).get('provider', 'none')
        
        print_with_timestamp(f"使用するLLMプロバイダ: {llm_provider}")
        print_with_timestamp(f"取得した論文: {paper.title}")
        
        # LLM処理
        if llm_provider == "gemini":
            paper = process_paper_with_gemini(paper)
        elif llm_provider == "chatgpt":
            paper = process_paper_with_chatgpt(paper)
        else:
            print_with_timestamp("LLMは使用しません")
        
        # メッセージのフォーマット
        message = format_paper_for_slack(paper)
        if not message:
            print_with_timestamp("メッセージのフォーマットに失敗しました。処理を終了します。")
            return
        
        # あいさつの追加とSlack送信
        message = add_greeting_to_message(message)
        result = send_to_slack(message)
        
        if result:
            print_with_timestamp("処理が正常に完了しました。")
        else:
            print_with_timestamp("Slackへの送信が失敗しましたが、処理は継続されました。")
            
    except Exception as e:
        print_with_timestamp(f"メイン処理中に予期しないエラーが発生しました: {e}")
        print_with_timestamp("処理を終了します。")

if __name__ == "__main__":
    main()
