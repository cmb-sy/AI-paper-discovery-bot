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
    api_key_env = config.get('gemini', {}).get('gemini_api_key_env', 'GEMINI_APIKEY')
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
        print_with_timestamp(f"Geminiによる処理中にエラーが発生しました: {e}")
        return paper 