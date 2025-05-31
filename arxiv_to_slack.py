import arxiv
import yaml
import logging
from datetime import datetime
import os
import sys
import time
import random
from slack_sdk.webhook import WebhookClient
from slack_sdk.errors import SlackApiError
from googletrans import Translator

logging.getLogger("httpx").setLevel(logging.WARNING) # 外部ライブラリのロギングを無効化

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arxiv_to_slack.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('arxiv_to_slack')

# 設定ファイルを読み込む
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
try:
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    print("設定ファイルを読み込みました: %s", CONFIG_PATH)
except Exception as e:
    print("設定ファイルの読み込みに失敗しました: %s", e)
    sys.exit(1)

# Slackのwebhook URL（環境変数から取得、なければconfigから）
SLACK_WEBHOOK_URL = os.environ.get('WEBHOOK_URL', config['slack']['webhook_url'])

# テストモードの確認（GitHub Actionsのpushイベントなどで使用）
TEST_MODE = os.environ.get('TEST_MODE', 'false').lower() == 'true'
if TEST_MODE:
    print("🧪 テストモードで実行しています")

# ChatGPT設定
USE_CHATGPT = config.get('chatgpt', {}).get('use_chatgpt', False)
CHATGPT_API_KEY = config.get('chatgpt', {}).get('api_key', os.environ.get('OPENAI_API_KEY', ''))
CHATGPT_MODEL = config.get('chatgpt', {}).get('model', 'gpt-3.5-turbo')
CHATGPT_TEMPERATURE = config.get('chatgpt', {}).get('temperature', 0.7)

# ChatGPTユーティリティのインポート
if USE_CHATGPT:
    try:
        from chatgpt_utils import process_paper_with_chatgpt
        logger.info("ChatGPTモードを有効化しました")
    except ImportError:
        logger.warning("ChatGPTユーティリティをインポートできませんでした。ChatGPTモードは無効になります。")
        USE_CHATGPT = False

# 検索する分野（AI関連）
AI_CATEGORIES = config['arxiv']['categories']

# 最大取得論文数
MAX_RESULTS = config['arxiv']['max_results']

# フィルタリング設定
FILTERS = config['arxiv'].get('filters', {})
MAX_YEARS_OLD = FILTERS.get('max_years_old', 3)
KEYWORDS = FILTERS.get('keywords', [])
FILTER_LOGIC = FILTERS.get('filter_logic', 'or')

def is_recent_paper(paper):
    """論文が指定された年数以内かどうかを確認する"""
    try:
        publish_date = paper.published
        years_old = (datetime.now() - publish_date).days / 365
        return years_old <= MAX_YEARS_OLD
    except Exception:
        # 日付が取得できない場合は通す
        return True

def contains_keywords(paper):
    """論文のタイトルまたは要約にキーワードが含まれているかを確認する"""
    if not KEYWORDS:
        return False
        
    title_and_summary = (paper.title + " " + paper.summary).lower()
    for keyword in KEYWORDS:
        if keyword.lower() in title_and_summary:
            return True
    return False

def filter_papers(papers):
    """論文をフィルタリングする"""
    filtered_papers = []
    original_count = len(papers)
    logger.info("論文フィルタリングを開始します（%d件）", original_count)
    
    for paper in papers:
        # 常に過去X年以内の論文に限定
        if not is_recent_paper(paper):
            continue
            
        # キーワードフィルタリング（キーワードがある場合）
        if KEYWORDS and not contains_keywords(paper):
            continue
            
        # 引用数の取得なしで論文を追加
        filtered_papers.append(paper)
    
    logger.info("フィルタリング完了: %d/%d件が条件を満たしました", 
             len(filtered_papers), original_count)
    
    return filtered_papers

def search_ai_papers():
    logger.info("ArXivからAI関連の論文の検索を開始します")
    try:
        # 最新のarxivライブラリに合わせた実装
        client = arxiv.Client()
        
        # カテゴリの検索クエリを作成
        category_query = " OR ".join(f"cat:{cat}" for cat in AI_CATEGORIES)
        
        # 日付指定は複雑なので、カテゴリのみで検索し、結果数を増やす
        query = f"({category_query})"
        
        logger.debug("検索クエリ: %s", query)
        
        # 検索実行
        search = arxiv.Search(
            query=query,
            max_results=MAX_RESULTS * 3,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        results = list(client.results(search))
        logger.info("%d件の論文が見つかりました", len(results))
        
        # 検索結果をフィルタリング（引用数でのフィルタリングなし）
        filtered_results = filter_papers(results)
        
        return filtered_results
    except Exception as e:
        logger.error("論文検索中にエラーが発生しました: %s", e)
        return []

def format_paper_for_slack(paper):
    """論文情報をSlack用にフォーマットする"""
    try:
        # 要約の改行を整形
        summary = ' '.join(paper.summary.split())
        
        # タイトルと要約を日本語に翻訳
        try:
            translator = Translator()
            translated_title = translator.translate(paper.title, dest='ja').text
            translated_summary = translator.translate(summary, dest='ja').text
            logger.info("論文タイトルと要約を日本語に翻訳しました")
        except Exception as e:
            logger.error(f"翻訳中にエラーが発生しました: {e}")
            translated_title = paper.title
            translated_summary = summary
        
        # Slack用のメッセージのブロックを作成
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": translated_title,
                    "emoji": True
                }
            },
        ]
        
        # ChatGPTによる処理結果があれば追加
        chatgpt_result = getattr(paper, 'chatgpt_result', None)
        if USE_CHATGPT and chatgpt_result:
            blocks.extend([
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*ChatGPTによる要約:*\n{chatgpt_result.get('summary', '')}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*重要性:*\n{chatgpt_result.get('importance', '')}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*応用可能性:*\n{chatgpt_result.get('applications', '')}"
                    }
                },
            ])
        else:
            # ChatGPTを使用しない場合は翻訳した概要を表示（文字数制限なし）
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*概要:*\n{translated_summary}"
                }
            })
        
        # リンクと区切り線を追加
        blocks.extend([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{paper.entry_id}|arXivはこちらから>"
                }
            },
            {
                "type": "divider"
            }
        ])
        
        # メッセージを作成
        message = {"blocks": blocks}
        return message
    except Exception as e:
        logger.error("論文のフォーマット中にエラーが発生しました: %s", e)
        return None

def send_to_slack(message):
    """Slackにメッセージを送信する"""
    try:
        # URLが設定されているか確認
        if not SLACK_WEBHOOK_URL:
            print("Slack webhook URLが設定されていません。WEBHOOK_URL環境変数またはconfig.yamlを確認してください。")
            return None
            
        webhook = WebhookClient(SLACK_WEBHOOK_URL)
        response = webhook.send(**message)
        print(f"Slackへの送信が完了しました。ステータスコード: {response.status_code}")
        return response
    except SlackApiError as e:
        logger.error("Slackへの送信中にAPIエラーが発生しました: %s", e)
        return None
    except Exception as e:
        logger.error("Slackへの送信中に予期しないエラーが発生しました: %s", e)
        print(f"エラーの詳細: {e}")
        return None

def main():
    """メイン関数"""
    logger.info("ArXiv to Slack 処理を開始します")
    papers = search_ai_papers()
    
    if not papers:
        logger.warning("論文が見つかりませんでした。")
        return
    
    # フィルタされた論文からランダムに1件選択する
    top_paper = random.choice(papers)
    logger.info("ランダムに選択された論文: %s", top_paper.title)
    
    # 引用数を表示する必要がなくなったので、取得しない
    # citation_count = get_citation_count(top_paper)
    # top_paper.citation_count = citation_count
    
    # ChatGPT APIを使用して論文を処理
    if USE_CHATGPT and CHATGPT_API_KEY:
        try:
            logger.info("ChatGPT APIを使用して論文を処理しています...")
            chatgpt_result = process_paper_with_chatgpt(
                top_paper, 
                CHATGPT_API_KEY,
                model=CHATGPT_MODEL,
                temperature=CHATGPT_TEMPERATURE
            )
            message = format_paper_for_slack(chatgpt_result)
        except Exception as e:
            logger.error(f"ChatGPTによる処理中にエラーが発生しました: {e}")
    else:
        message = format_paper_for_slack(top_paper)

    # メッセージのブロックの先頭に文章を追加
    if message and "blocks" in message:
        message["blocks"].insert(0, {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "おはよう☀️ 今日の論文はこちら!!"
            }
        })
        
    send_to_slack(message)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("ユーザーによって処理が中断されました")
        sys.exit(0)
    except Exception as e:
        logger.critical("予期しないエラーが発生しました: %s", e, exc_info=True)
        sys.exit(1)
