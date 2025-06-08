"""
論文情報のフォーマットと翻訳を行うモジュール
"""
from googletrans import Translator
from .config_loader import get_config
from .utils import print_with_timestamp

def clean_text(text):
    return ' '.join(text.split())

def translate_text(text, dest_lang='ja'):
    config = get_config()
    use_translation = config.get('translation', {}).get('enabled', True)
    if not use_translation:
        print_with_timestamp("翻訳設定が無効なため、原文のまま表示します")
        return text
    try:
        translator = Translator()
        translated = translator.translate(text, dest=dest_lang).text
        return translated
    except Exception as e:
        print_with_timestamp(f"翻訳中にエラーが発生しました: {e}")
        return text

def format_paper_for_slack(paper):
    config = get_config()
    use_translation = config.get('translation', {}).get('enabled', True)
    llm_provider = config.get('llm', {}).get('provider', 'none')
    
    try:
        title = clean_text(paper.title)
        summary = clean_text(paper.summary)
        
        # LLMを使用する場合は翻訳をスキップ
        if llm_provider != "none":
            print_with_timestamp(f"{llm_provider}を使用するため、原文のまま表示します")
            translated_title = title
            translated_summary = summary
        elif use_translation:
            try:
                translator = Translator()
                translated_title = translator.translate(title, dest='ja').text
                translated_summary = translator.translate(summary, dest='ja').text
                print_with_timestamp("論文タイトルと要約を日本語に翻訳しました")
            except Exception as e:
                print_with_timestamp(f"翻訳中にエラーが発生しました: {e}")
                translated_title = title
                translated_summary = summary
        else:
            print_with_timestamp("翻訳設定が無効なため、原文のまま表示します")
            translated_title = title
            translated_summary = summary
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
        
        # LLMプロバイダに基づく処理
        llm_result = None
        llm_error = False
        
        if llm_provider == "gemini":
            llm_result = getattr(paper, 'gemini_result', None)
            llm_name = "Gemini"
        elif llm_provider == "chatgpt":
            llm_result = getattr(paper, 'chatgpt_result', None)
            llm_name = "ChatGPT"
        
        if llm_provider != "none":
            # LLMの結果がある場合
            if llm_result:
                # エラーメッセージがある場合（"※"で始まる場合はエラー）
                if llm_result.startswith("※"):
                    llm_error = True
                    blocks.extend([
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*{llm_name}処理エラー:*\n{llm_result}"
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*元の概要:*\n{translated_summary}"
                            }
                        }
                    ])
                # 正常に要約された場合
                else:
                    blocks.extend([
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*{llm_name}による要約:*\n{llm_result}"
                            }
                        }
                    ])
            # LLM結果がない場合は通常の概要を表示
            else:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*概要:*\n{translated_summary}"
                    }
                })
        # LLMを使用しない場合
        else:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*概要:*\n{translated_summary}"
                }
            })
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
        message = {"blocks": blocks}
        return message
    except Exception as e:
        print_with_timestamp(f"論文のフォーマット中にエラーが発生しました: {e}")
        return None
