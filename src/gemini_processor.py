"""
Gemini 1.5 Proによる論文処理を行うモジュール
"""
import os
import google.generativeai as genai
from src.config_loader import get_config
from src.utils import print_with_timestamp

def process_paper_with_gemini(paper):
    config = get_config()
    use_gemini = config.get('gemini', {}).get('use_gemini', False)
    api_key_env = config.get('gemini', {}).get('gemini_api_key_env', 'GEMINI_API_KEY')
    api_key = os.environ.get(api_key_env, '')
    model_name = config.get('gemini', {}).get('model', 'models/gemini-1.5-pro-latest')
    temperature = config.get('gemini', {}).get('temperature', 0.7)

    if not use_gemini or not api_key:
        return paper

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        title = ' '.join(paper.title.split())
        abstract = ' '.join(paper.summary.split())
        prompt = f"""以下の論文を日本語で要約し、要点を以下のフォーマットに従って800~1000文字で出力してください。

タイトル: {title}
アブストラクト:
{abstract}

<問題設定>

<提案手法>

<結果>

<結論>
"""
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