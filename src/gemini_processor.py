"""
Gemini 1.5 Proによる論文処理を行うモジュール
"""
import os
import re
import requests
import PyPDF2
from io import BytesIO
import google.generativeai as genai
from src.config_loader import get_config
from src.utils import print_with_timestamp

def extract_intelligent_content(paper):
    """論文から重要なセクションを賢く抽出"""
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
        all_text = ""
        
        # 全ページのテキストを結合
        for page in pdf_reader.pages:
            all_text += page.extract_text() + "\n"
        
        # セクション情報を抽出
        extracted_info = {
            'total_pages': total_pages,
            'introduction': extract_section(all_text, ['introduction', '1.', 'はじめに', '序論']),
            'method': extract_section(all_text, ['method', 'approach', '手法', '方法', 'methodology']),
            'results': extract_section(all_text, ['result', 'experiment', '実験', '結果', 'evaluation']),
            'conclusion': extract_section(all_text, ['conclusion', 'discussion', '結論', '考察', 'まとめ']),
            'keywords': extract_keywords(all_text),
            'figures_tables': extract_figures_and_tables(all_text)
        }
        
        # 構造化された情報を構築
        structured_content = build_structured_content(extracted_info)
        
        print_with_timestamp(f"PDF処理完了: {total_pages}ページから重要セクションを抽出")
        return structured_content[:6000]  # トークン制限を少し拡張
        
    except Exception as e:
        print_with_timestamp(f"PDF処理エラー: {e}")
        return ""

def extract_section(text, keywords):
    """特定のセクションをキーワードベースで抽出"""
    text_lower = text.lower()
    
    for keyword in keywords:
        # セクションヘッダーを探す
        pattern = rf'(?:^|\n)\s*(?:\d+\.?\s*)?{re.escape(keyword.lower())}.*?\n(.*?)(?=\n\s*(?:\d+\.?\s*)?[a-zA-Z]|$)'
        match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
        
        if match:
            section_text = match.group(1).strip()
            # 最初の500文字程度を返す
            return section_text[:500] if section_text else ""
    
    return ""

def extract_keywords(text):
    """論文からキーワードを抽出"""
    # Keywords, キーワード, Index Terms などの後に続く単語を抽出
    keyword_patterns = [
        r'(?:keywords?|キーワード|index terms?)[:\s]*([^\n.]+)',
        r'(?:terms?|用語)[:\s]*([^\n.]+)'
    ]
    
    keywords = []
    for pattern in keyword_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # カンマやセミコロンで分割
            terms = re.split(r'[,;]', match)
            keywords.extend([term.strip() for term in terms if term.strip()])
    
    # 上位5つのキーワードを返す
    return keywords[:5]

def extract_figures_and_tables(text):
    """図表のキャプションを抽出"""
    # Figure, Table, Fig, 図, 表 などのキャプションを抽出
    caption_patterns = [
        r'(?:figure?|fig\.?|図)\s*\d+[:\.]?\s*([^\n]+)',
        r'(?:table|表)\s*\d+[:\.]?\s*([^\n]+)'
    ]
    
    captions = []
    for pattern in caption_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        captions.extend(matches[:2])  # 各タイプから最大2つ
    
    return captions[:4]  # 合計最大4つのキャプション

def build_structured_content(info):
    """抽出した情報を構造化して文字列に変換"""
    content = f"=== 論文構造情報 ===\n"
    content += f"総ページ数: {info['total_pages']}ページ\n\n"
    
    if info['keywords']:
        content += f"=== キーワード ===\n"
        content += f"{', '.join(info['keywords'])}\n\n"
    
    if info['introduction']:
        content += f"=== 序論・はじめに ===\n"
        content += f"{info['introduction']}\n\n"
    
    if info['method']:
        content += f"=== 手法・アプローチ ===\n"
        content += f"{info['method']}\n\n"
    
    if info['results']:
        content += f"=== 実験結果 ===\n"
        content += f"{info['results']}\n\n"
    
    if info['conclusion']:
        content += f"=== 結論・考察 ===\n"
        content += f"{info['conclusion']}\n\n"
    
    if info['figures_tables']:
        content += f"=== 図表情報 ===\n"
        for i, caption in enumerate(info['figures_tables'], 1):
            content += f"{i}. {caption}\n"
        content += "\n"
    
    return content

def extract_first_and_last_pages(paper):
    """PDFの最初と最後のページのテキストを抽出（後方互換性のため保持）"""
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

def process_paper_with_gemini(paper):
    config = get_config()
    api_key_env = config.get('gemini', {}).get('gemini_api_key_env', 'GEMINI_API_KEY')
    api_key = os.environ.get(api_key_env, '')
    model_name = config.get('gemini', {}).get('model', 'models/gemini-1.5-pro-latest')
    temperature = config.get('gemini', {}).get('temperature', 0.7)

    if not api_key:
        return paper

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        title = ' '.join(paper.title.split())
        abstract = ' '.join(paper.summary.split())
        
        # 著者情報の取得
        authors = ", ".join([author.name for author in paper.authors]) if paper.authors else "不明"
        
        # 公開日の取得
        published_date = paper.published.strftime("%Y年%m月%d日") if paper.published else "不明"
        
        # カテゴリの取得
        categories = ", ".join(paper.categories) if paper.categories else "不明"
        
        # PDFから重要なセクションを知的に抽出
        pdf_content = extract_intelligent_content(paper)
        
        prompt = f"""あなたは論文解析の専門家です。以下の論文を日本語で分析し、要点を整理して出力してください。

【論文情報】
タイトル: {title}
著者: {authors}
公開日: {published_date}
カテゴリ: {categories}

【アブストラクト】
{abstract}

{pdf_content if pdf_content else ""}

【分析指示】
以下の5つの観点から論文を分析し、各項目80～120文字で簡潔にまとめてください。
専門用語は必要に応じて分かりやすく説明を加えてください。

1. 📄 研究概要: この論文が何について研究しているのか、全体像を一言で要約
2. 🎯 解決する課題: どのような問題や課題に取り組んでいるのか
3. 💡 提案手法: 問題解決のためにどのような新しいアプローチや手法を提案しているのか
4. 📊 主要な結果: 実験や検証でどのような成果が得られたのか（数値があれば含める）
5. 📝 意義・インパクト: この研究が学術界や実社会にどのような影響を与えるのか

【出力形式】
Slack形式で出力してください（太文字は *テキスト* で表現、区切り線は --- を使用）

*📄 研究概要*
[内容]

---

*🎯 解決する課題*
[内容]

---

*💡 提案手法*
[内容]

---

*📊 主要な結果*
[内容]

---

*📝 意義・インパクト*
[内容]

【注意事項】
- 各項目は独立して理解できるように記述
- 専門用語には簡潔な説明を併記
- 客観的かつ正確な情報のみを記述
- 初学者にも理解できるように配慮
- 推測や憶測は避ける"""
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": 2048
            }
        )
        paper.gemini_result = response.text
        print_with_timestamp("Gemini APIで要約を生成しました")
        return paper
    except Exception as e:
        error_message = str(e).lower()
        
        # 利用制限に関連するエラーメッセージを検出
        if "rate limit" in error_message or "quota" in error_message or "exceeded" in error_message:
            print_with_timestamp("⚠️ Gemini APIの利用制限に達しました。しばらく時間を置いてから再試行してください。")
            print_with_timestamp(f"詳細エラー: {e}")
            paper.gemini_result = "※ Gemini APIの利用制限に達したため、要約を生成できませんでした。"
        elif "permission" in error_message or "access" in error_message or "unauthorized" in error_message:
            print_with_timestamp("⚠️ Gemini APIへのアクセス権限がありません。APIキーを確認してください。")
            print_with_timestamp(f"詳細エラー: {e}")
            paper.gemini_result = "※ Gemini APIのアクセス権限エラーが発生したため、要約を生成できませんでした。"
        elif "invalid" in error_message and "api" in error_message and "key" in error_message:
            print_with_timestamp("⚠️ Gemini APIキーが無効です。正しいAPIキーを設定してください。")
            print_with_timestamp(f"詳細エラー: {e}")
            paper.gemini_result = "※ 無効なGemini APIキーのため、要約を生成できませんでした。"
        else:
            print_with_timestamp(f"Geminiによる処理中にエラーが発生しました: {e}")
            paper.gemini_result = "※ Gemini API処理中にエラーが発生したため、要約を生成できませんでした。"
        
        return paper 