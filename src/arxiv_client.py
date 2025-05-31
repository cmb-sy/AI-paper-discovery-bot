"""
arXivからの論文検索と取得を行うモジュール
"""
import arxiv
from datetime import datetime
import random
from .config_loader import get_config
from .utils import print_with_timestamp

def is_recent_paper(paper, max_years_old):
    try:
        publish_date = paper.published
        years_old = (datetime.now() - publish_date).days / 365
        return years_old <= max_years_old
    except Exception:
        # 日付が取得できない場合は通す
        return True

def contains_keywords(paper, keywords):
    if not keywords:
        return False
        
    title_and_summary = (paper.title + " " + paper.summary).lower()
    return any(keyword.lower() in title_and_summary for keyword in keywords)

def filter_papers(papers, max_years_old, keywords):
    original_count = len(papers)
    print_with_timestamp(f"論文フィルタリングを開始します（{original_count}件）")
    
    filtered_papers = [
        paper for paper in papers 
        if is_recent_paper(paper, max_years_old) and (not keywords or contains_keywords(paper, keywords))
    ]
    
    return filtered_papers

def search_ai_papers():
    config = get_config()
    
    # 設定から検索条件を取得
    ai_categories = config['arxiv']['categories']
    max_results = config['arxiv']['max_results']
    filters = config['arxiv'].get('filters', {})
    max_years_old = filters.get('max_years_old', 3)
    keywords = filters.get('keywords', [])
    
    print_with_timestamp("ArXivからAI関連の論文の検索を開始します")
    try:
        client = arxiv.Client() # 最新のarxivライブラリに合わせた実装
        category_query = " OR ".join(f"cat:{cat}" for cat in ai_categories) # カテゴリの検索クエリを作成
        query = f"({category_query})" # 日付指定は複雑なので、カテゴリのみで検索し、結果数を増やす
        
        search = arxiv.Search(
            query=query,
            max_results=max_results * 3,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        results = list(client.results(search))
        filtered_results = filter_papers(results, max_years_old, keywords)
        return filtered_results
    except Exception as e:
        print_with_timestamp(f"論文検索中にエラーが発生しました: {e}")
        return []

def get_random_paper():
    papers = search_ai_papers()
    if not papers:
        print_with_timestamp("論文が見つかりませんでした。")
        return None    
    paper = random.choice(papers)
    
    return paper
