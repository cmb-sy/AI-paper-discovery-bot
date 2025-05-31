import arxiv
import yaml
from datetime import datetime
import os
import sys
import random
from slack_sdk.webhook import WebhookClient
from slack_sdk.errors import SlackApiError
from googletrans import Translator

# 現在時刻を取得する関数
def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 設定ファイルを読み込む
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
try:
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    print(f"{get_timestamp()} - 設定ファイルを読み込みました: {CONFIG_PATH}")
except Exception as e:
    print(f"{get_timestamp()} - 設定ファイルの読み込みに失敗しました: {e}")
    sys.exit(1)

# Slackのwebhook URL（環境変数から取得、なければconfigから）
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# ChatGPT設定
USE_CHATGPT = config.get('chatgpt', {}).get('use_chatgpt', False)
CHATGPT_API_KEY = config.get('chatgpt', {}).get('api_key', os.environ.get('OPENAI_API_KEY', ''))
CHATGPT_MODEL = config.get('chatgpt', {}).get('model', 'gpt-3.5-turbo')
CHATGPT_TEMPERATURE = config.get('chatgpt', {}).get('temperature', 0.7)

# 翻訳設定
USE_TRANSLATION = config.get('translation', {}).get('enabled', True)  # デフォルトはTrue

# ChatGPTユーティリティのインポート
if USE_CHATGPT:
    try:
        from chatgpt_utils import process_paper_with_chatgpt
        print(f"{get_timestamp()} - ChatGPTモードを有効化しました")
    except ImportError:
        print(f"{get_timestamp()} - ChatGPTユーティリティをインポートできませんでした。ChatGPTモードは無効になります。")
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
    return any(keyword.lower() in title_and_summary for keyword in KEYWORDS)

def filter_papers(papers):
    """論文をフィルタリングする"""
    filtered_papers = []
    original_count = len(papers)
    print(f"{get_timestamp()} - 論文フィルタリングを開始します（{original_count}件）")
    
    filtered_papers = [paper for paper in papers if is_recent_paper(paper) and (not KEYWORDS or contains_keywords(paper))]
    
    print(f"{get_timestamp()} - フィルタリング完了: {len(filtered_papers)}/{original_count}件が条件を満たしました")
    
    return filtered_papers

def search_ai_papers():
    """ArXivからAI関連の論文を検索する"""
    print(f"{get_timestamp()} - ArXivからAI関連の論文の検索を開始します")
    try:
        # 最新のarxivライブラリに合わせた実装
        client = arxiv.Client()
        
        # カテゴリの検索クエリを作成
        category_query = " OR ".join(f"cat:{cat}" for cat in AI_CATEGORIES)
        
        # 日付指定は複雑なので、カテゴリのみで検索し、結果数を増やす
        query = f"({category_query})"
        
        print(f"{get_timestamp()} - 検索クエリ: {query}")
        
        # 検索実行
        search = arxiv.Search(
            query=query,
            max_results=MAX_RESULTS * 3,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        results = list(client.results(search))
        print(f"{get_timestamp()} - {len(results)}件の論文が見つかりました")
        
        # 検索結果をフィルタリング
        filtered_results = filter_papers(results)
        
        return filtered_results
    except Exception as e:
        print(f"{get_timestamp()} - 論文検索中にエラーが発生しました: {e}")
        return []

def format_paper_for_slack(paper):
    """論文情報をSlack用にフォーマットする"""
    try:
        # 論文タイトルと要約の改行を整形
        title = ' '.join(paper.title.split())
        summary = ' '.join(paper.summary.split())
        
        # 設定に基づいて翻訳を行う
        if USE_TRANSLATION:
            try:
                translator = Translator()
                translated_title = translator.translate(title, dest='ja').text
                translated_summary = translator.translate(summary, dest='ja').text
                print(f"{get_timestamp()} - 論文タイトルと要約を日本語に翻訳しました")
            except Exception as e:
                print(f"{get_timestamp()} - 翻訳中にエラーが発生しました: {e}")
                translated_title = title
                translated_summary = summary
        else:
            print(f"{get_timestamp()} - 翻訳設定が無効なため、原文のまま表示します")
            translated_title = title
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
            # ChatGPTを使用しない場合は翻訳した概要を表示
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
        print(f"{get_timestamp()} - 論文のフォーマット中にエラーが発生しました: {e}")
        return None

def send_to_slack(message):
    """Slackにメッセージを送信する"""
    try:
        # URLが設定されているか確認
        if not SLACK_WEBHOOK_URL:
            print(f"{get_timestamp()} - Slack webhook URLが設定されていません。WEBHOOK_URL環境変数またはconfig.yamlを確認してください。")
            return None
            
        webhook = WebhookClient(SLACK_WEBHOOK_URL)
        response = webhook.send(**message)
        print(f"{get_timestamp()} - Slackへの送信が完了しました。ステータスコード: {response.status_code}")
        return response
    except SlackApiError as e:
        print(f"{get_timestamp()} - Slackへの送信中にAPIエラーが発生しました: {e}")
        return None
    except Exception as e:
        print(f"{get_timestamp()} - Slackへの送信中に予期しないエラーが発生しました: {e}")
        return None

def main():
    """メイン関数"""
    print(f"{get_timestamp()} - ArXiv to Slack 処理を開始します")
    papers = search_ai_papers()
    
    if not papers:
        print(f"{get_timestamp()} - 論文が見つかりませんでした。")
        return
    
    # フィルタされた論文からランダムに1件選択する
    top_paper = random.choice(papers)
    print(f"{get_timestamp()} - ランダムに選択された論文: {top_paper.title}")
    
    # ChatGPT APIを使用して論文を処理
    if USE_CHATGPT and CHATGPT_API_KEY:
        try:
            print(f"{get_timestamp()} - ChatGPT APIを使用して論文を処理しています...")
            chatgpt_result = process_paper_with_chatgpt(
                top_paper, 
                CHATGPT_API_KEY,
                model=CHATGPT_MODEL,
                temperature=CHATGPT_TEMPERATURE
            )
            top_paper.chatgpt_result = chatgpt_result
        except Exception as e:
            print(f"{get_timestamp()} - ChatGPTによる処理中にエラーが発生しました: {e}")
    
    # Slackメッセージを作成
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
        print(f"{get_timestamp()} - ユーザーによって処理が中断されました")
        sys.exit(0)
    except Exception as e:
        print(f"{get_timestamp()} - 予期しないエラーが発生しました: {e}")
        sys.exit(1)
