"""
ChatGPTによる論文処理を行うモジュール
"""
import os
import openai
from src.config_loader import get_config
from src.utils import print_with_timestamp

def process_paper_with_chatgpt(paper):
    config = get_config()
    api_key_env = config.get('chatgpt', {}).get('openai_api_key_env', 'OPENAI_API_KEY')
    api_key = os.environ.get(api_key_env, '')
    model_name = config.get('chatgpt', {}).get('model', 'gpt-4o')
    temperature = config.get('chatgpt', {}).get('temperature', 0.7)

    if not api_key:
        print_with_timestamp("OpenAI APIキーが設定されていません。ChatGPTによる処理をスキップします。")
        return paper

    try:
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        
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
        response = client.chat.completions.create(
            model=model_name,
            temperature=temperature,
            messages=[
                {"role": "system", "content": "あなたは研究論文を分析する専門家のAIアシスタントです。"},
                {"role": "user", "content": prompt}
            ],
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
