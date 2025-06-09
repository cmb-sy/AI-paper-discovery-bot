"""
arXivからの論文検索と取得を行うモジュール
"""
import arxiv
from datetime import datetime
import random
import time
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

def search_ai_papers_with_retry(max_retries=3, delay=2):
    """リトライ機能付きのArXiv検索（高速化版）"""
    config = get_config()
    
    # 設定から検索条件を取得
    ai_categories = config['arxiv']['categories']
    max_results = min(config['arxiv']['max_results'], 50)  # 結果数を制限して高速化
    filters = config['arxiv'].get('filters', {})
    max_years_old = filters.get('max_years_old', 3)
    keywords = filters.get('keywords', [])
    
    print_with_timestamp("ArXivからAI関連の論文の検索を開始します（高速化モード）")
    
    for attempt in range(max_retries):
        try:
            print_with_timestamp(f"検索試行 {attempt + 1}/{max_retries}")
            
            # より軽量なクライアント設定
            client = arxiv.Client(
                page_size=10,  # 小さなページサイズ
                delay_seconds=0.5,  # より短い遅延
                num_retries=1  # 少ないリトライ
            )
            
            # より具体的なクエリでヒット数を絞る
            if keywords:
                keyword_query = " OR ".join(f'"{keyword}"' for keyword in keywords[:3])  # 上位3つのキーワードのみ
                category_query = " OR ".join(f"cat:{cat}" for cat in ai_categories)
                query = f"({category_query}) AND ({keyword_query})"
            else:
                category_query = " OR ".join(f"cat:{cat}" for cat in ai_categories)
                query = f"({category_query})"
            
            print_with_timestamp(f"検索クエリ: {query}")
            
            search = arxiv.Search(
                query=query,
                max_results=max_results,  # より小さい結果セット
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            # タイムアウト付きで結果を取得
            results = []
            count = 0
            timeout_start = time.time()
            timeout_duration = 30  # 30秒でタイムアウト
            
            for result in client.results(search):
                results.append(result)
                count += 1
                
                # タイムアウトチェック
                if time.time() - timeout_start > timeout_duration:
                    print_with_timestamp(f"タイムアウト: {count}件の論文を取得済み")
                    break
                    
                if count >= max_results:
                    break
                
            print_with_timestamp(f"ArXivから {len(results)} 件の論文を取得しました")
            
            if results:
                filtered_results = filter_papers(results, max_years_old, keywords)
                print_with_timestamp(f"フィルタリング後: {len(filtered_results)} 件の論文")
                return filtered_results
            else:
                print_with_timestamp("検索結果が空でした")
                
        except Exception as e:
            error_msg = str(e)
            print_with_timestamp(f"試行 {attempt + 1} で論文検索中にエラーが発生: {error_msg}")
            
            # 特定のエラータイプに応じた対応
            if "Connection" in error_msg or "timeout" in error_msg.lower():
                if attempt < max_retries - 1:
                    wait_time = delay * (attempt + 1)  # 線形バックオフ（高速化）
                    print_with_timestamp(f"ネットワークエラーのため {wait_time} 秒待機してリトライします...")
                    time.sleep(wait_time)
                    continue
            elif "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
                if attempt < max_retries - 1:
                    wait_time = delay * 2
                    print_with_timestamp(f"レート制限のため {wait_time} 秒待機してリトライします...")
                    time.sleep(wait_time)
                    continue
            else:
                print_with_timestamp(f"予期しないエラー: {error_msg}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    continue
    
    print_with_timestamp("すべてのリトライが失敗しました")
    return []

def search_ai_papers():
    """従来の関数を維持（後方互換性）"""
    return search_ai_papers_with_retry()

def get_random_paper():
    """論文をランダムに選択して返す"""
    papers = search_ai_papers_with_retry()
    if not papers:
        print_with_timestamp("論文が見つかりませんでした。")
        return None    
    
    selected_paper = random.choice(papers)
    print_with_timestamp(f"選択された論文: {selected_paper.title[:100]}...")
    
    return selected_paper
