#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import arxiv
import json
import requests
import yaml
import logging
import re
from datetime import datetime, timedelta
import os
import sys
import time
from slack_sdk.webhook import WebhookClient
from slack_sdk.errors import SlackApiError
from semanticscholar import SemanticScholar

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
    logger.info("設定ファイルを読み込みました: %s", CONFIG_PATH)
except Exception as e:
    logger.error("設定ファイルの読み込みに失敗しました: %s", e)
    sys.exit(1)

# Slackのwebhook URL
SLACK_WEBHOOK_URL = config['slack']['webhook_url']

# 検索する分野（AI関連）
AI_CATEGORIES = config['arxiv']['categories']

# 最大取得論文数
MAX_RESULTS = config['arxiv']['max_results']

# 何日前の論文を検索するか
DAYS_BACK = config['arxiv']['days_back']

# フィルタリング設定
FILTERS = config['arxiv'].get('filters', {})
MAX_YEARS_OLD = FILTERS.get('max_years_old', 3)
KEYWORDS = FILTERS.get('keywords', [])
MIN_CITATIONS = FILTERS.get('min_citations', 10)
FILTER_LOGIC = FILTERS.get('filter_logic', 'or')

# Semantic Scholar API クライアント
sch = SemanticScholar()

def get_target_date():
    """対象日の日付を取得する"""
    target_date = datetime.now() - timedelta(days=DAYS_BACK)
    return target_date.strftime('%Y%m%d')

def get_citation_count(paper):
    """論文の引用数を取得する"""
    try:
        # arXiv IDから引用情報を取得
        arxiv_id = paper.entry_id.split('/')[-1]
        if 'v' in arxiv_id:
            arxiv_id = arxiv_id.split('v')[0]  # versionを除去
            
        paper_data = sch.get_paper(f'arXiv:{arxiv_id}')
        if paper_data and hasattr(paper_data, 'citationCount'):
            return paper_data.citationCount
        return 0
    except Exception as e:
        logger.warning(f"引用数の取得に失敗しました（{paper.title}）: {e}")
        return 0

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
            
        # 引用数を取得（APIコール回数を減らすため、必要な場合のみ）
        citation_count = 0
        if FILTER_LOGIC == "or" and contains_keywords(paper):
            # ORロジックでキーワードに一致する場合は引用数チェック不要
            paper.citation_count = 0
            filtered_papers.append(paper)
            continue
            
        # 引用数を取得
        citation_count = get_citation_count(paper)
        paper.citation_count = citation_count  # paperオブジェクトに追加
        
        if FILTER_LOGIC == "and":
            # ANDロジック: キーワードと引用数の両方を満たす必要がある
            if contains_keywords(paper) and citation_count >= MIN_CITATIONS:
                filtered_papers.append(paper)
        else:
            # ORロジック: キーワードを満たすか、引用数を満たす
            if citation_count >= MIN_CITATIONS:
                filtered_papers.append(paper)
    
    logger.info("フィルタリング完了: %d/%d件が条件を満たしました", 
             len(filtered_papers), original_count)
    return filtered_papers

def search_ai_papers():
    """ArXivからAI関連の論文を検索する"""
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
            max_results=MAX_RESULTS * 3,  # より多くの結果を取得してから選別
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        results = list(client.results(search))
        logger.info("%d件の論文が見つかりました", len(results))
        
        # 検索結果をフィルタリング
        filtered_results = filter_papers(results)
        
        # 設定した最大件数まで返す
        return filtered_results[:MAX_RESULTS]
    except Exception as e:
        logger.error("論文検索中にエラーが発生しました: %s", e)
        return []

def format_paper_for_slack(paper):
    """論文情報をSlack用にフォーマットする"""
    try:
        # 著者のリストを取得
        authors = ", ".join(author.name for author in paper.authors)
        
        # カテゴリのリストを取得
        categories = ", ".join(paper.categories)
        
        # 出版日を取得
        pub_date = paper.published.strftime("%Y-%m-%d") if hasattr(paper, "published") else "不明"
        
        # 引用数を取得（フィルタリング時に既に設定済み）
        citation_count = getattr(paper, 'citation_count', 0)
        
        # Slack用のメッセージを作成
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": paper.title,
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*著者:*\n{authors}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*カテゴリ:*\n{categories}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*出版日:*\n{pub_date}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*引用数:*\n{citation_count}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*概要:*\n{paper.summary[:300]}..." if len(paper.summary) > 300 else f"*概要:*\n{paper.summary}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*論文リンク:* <{paper.pdf_url}|PDF> | <{paper.entry_id}|arXiv>"
                    }
                },
                {
                    "type": "divider"
                }
            ]
        }
        
        return message
    except Exception as e:
        logger.error("論文のフォーマット中にエラーが発生しました: %s", e)
        return None

def send_to_slack(message):
    """Slackにメッセージを送信する"""
    try:
        webhook = WebhookClient(SLACK_WEBHOOK_URL)
        response = webhook.send(**message)
        return response
    except SlackApiError as e:
        logger.error("Slackへの送信中にAPIエラーが発生しました: %s", e)
        return None
    except Exception as e:
        logger.error("Slackへの送信中に予期しないエラーが発生しました: %s", e)
        return None

def main():
    """メイン関数"""
    logger.info("ArXiv to Slack 処理を開始します")
    start_time = time.time()
    
    papers = search_ai_papers()
    
    if not papers:
        logger.warning("論文が見つかりませんでした。")
        return
    
    logger.info("%d件の論文をSlackに投稿します", len(papers))
    
    success_count = 0
    for paper in papers:
        message = format_paper_for_slack(paper)
        if not message:
            continue
            
        response = send_to_slack(message)
        
        if response and response.status_code == 200:
            logger.info("論文「%s」を投稿しました", paper.title)
            success_count += 1
        else:
            logger.error("論文「%s」の投稿に失敗しました。ステータスコード: %s", 
                      paper.title, response.status_code if response else "不明")
        
        # API制限を防ぐために少し待機
        time.sleep(1)
    
    elapsed_time = time.time() - start_time
    logger.info("完了しました。%d/%d件の論文を送信しました（処理時間: %.2f秒）", 
             success_count, len(papers), elapsed_time)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("ユーザーによって処理が中断されました")
        sys.exit(0)
    except Exception as e:
        logger.critical("予期しないエラーが発生しました: %s", e, exc_info=True)
        sys.exit(1)
