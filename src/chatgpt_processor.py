"""
ChatGPTによる論文処理を行うモジュール
"""
import os
import requests
import PyPDF2
from io import BytesIO
import openai
from src.config_loader import get_config
from src.utils import print_with_timestamp

def extract_first_and_last_pages(paper):
    """PDFの最初と最後のページのテキストを抽出"""
    try:
        print_with_timestamp("PDFをダウンロード中...")
        
        # PDFのダウンロード
        pdf_url = paper.pdf_url
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        
        # PDFからテキスト抽出
        pdf_file = BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        total_pages = len(pdf_reader.pages)
        extracted_text = ""
        
        if total_pages > 0:
            # 最初のページ
            first_page = pdf_reader.pages[0]
            first_page_text = first_page.extract_text()
            extracted_text += f"=== 最初のページ ===\n{first_page_text}\n\n"
            
            # 最後のページ（最初のページと異なる場合のみ）
            if total_pages > 1:
                last_page = pdf_reader.pages[-1]
                last_page_text = last_page.extract_text()
                extracted_text += f"=== 最後のページ ===\n{last_page_text}"
        
        print_with_timestamp(f"PDF処理完了: {total_pages}ページ中、最初と最後のページを抽出")
        return extracted_text[:4000]  # トークン制限対策で4000文字まで
        
    except Exception as e:
        print_with_timestamp(f"PDF処理エラー: {e}")
        return ""

def process_paper_with_chatgpt(paper):
    config = get_config()
    api_key = os.environ.get('OPENAI_API_KEY', '')
    model_name = config.get('chatgpt', {}).get('model', 'gpt-3.5-turbo')
    temperature = config.get('chatgpt', {}).get('temperature', 0.7)

    if not api_key:
        print_with_timestamp("OpenAI APIキーが設定されていません。ChatGPTによる処理をスキップします。")
        return paper

    try:
        openai.api_key = api_key
        title = ' '.join(paper.title.split())
        abstract = ' '.join(paper.summary.split())
        
        # 著者情報の取得
        authors = ", ".join([author.name for author in paper.authors]) if paper.authors else "不明"
        
        # 公開日の取得
        published_date = paper.published.strftime("%Y年%m月%d日") if paper.published else "不明"
        
        # カテゴリの取得
        categories = ", ".join(paper.categories) if paper.categories else "不明"
        
        # PDFの最初と最後のページを取得
        pdf_content = extract_first_and_last_pages(paper)
        
        prompt = f"""以下の論文を日本語で要約し、要点を以下のフォーマットに従って500~800文字で出力してください

## タイトル
{title}

## 著者
{authors}

## 公開日
{published_date}

## カテゴリ
{categories}

## アブストラクト（原文）
{abstract}

{pdf_content if pdf_content else ""}

## アブストラクト

## 問題設定

## 提案手法

## 結果

## 結論
"""
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=2048
        )
        paper.chatgpt_result = response.choices[0].message.content
        print_with_timestamp("ChatGPT APIで要約を生成しました")
        return paper
    except Exception as e:
        error_message = str(e).lower()
        
        # 利用制限に関連するエラーメッセージを検出
        if "rate limit" in error_message or "quota" in error_message or "exceeded" in error_message:
            print_with_timestamp("⚠️ OpenAI APIの利用制限に達しました。しばらく時間を置いてから再試行してください。")
            print_with_timestamp(f"詳細エラー: {e}")
            paper.chatgpt_result = "※ OpenAI APIの利用制限に達したため、要約を生成できませんでした。"
        elif "permission" in error_message or "access" in error_message or "unauthorized" in error_message:
            print_with_timestamp("⚠️ OpenAI APIへのアクセス権限がありません。APIキーを確認してください。")
            print_with_timestamp(f"詳細エラー: {e}")
            paper.chatgpt_result = "※ OpenAI APIのアクセス権限エラーが発生したため、要約を生成できませんでした。"
        elif "invalid" in error_message and "api" in error_message and "key" in error_message:
            print_with_timestamp("⚠️ OpenAI APIキーが無効です。正しいAPIキーを設定してください。")
            print_with_timestamp(f"詳細エラー: {e}")
            paper.chatgpt_result = "※ 無効なOpenAI APIキーのため、要約を生成できませんでした。"
        else:
            print_with_timestamp(f"ChatGPTによる処理中にエラーが発生しました: {e}")
            paper.chatgpt_result = "※ OpenAI API処理中にエラーが発生したため、要約を生成できませんでした。"
        
        return paper
