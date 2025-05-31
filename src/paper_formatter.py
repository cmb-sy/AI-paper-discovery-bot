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
    use_chatgpt = config.get('chatgpt', {}).get('use_chatgpt', False)
    
    try:
        # 論文タイトルと要約の改行を整形
        title = clean_text(paper.title)
        summary = clean_text(paper.summary)
        
        # ChatGPTを使う場合は翻訳しない
        if use_chatgpt:
            print_with_timestamp("ChatGPTを使用するため、原文のまま表示します")
            translated_title = title
            translated_summary = summary
            
        # ChatGPTを使わない場合は設定に基づいて翻訳を行う
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
        
        chatgpt_result = getattr(paper, 'chatgpt_result', None)
        if use_chatgpt and chatgpt_result:
            blocks.extend([
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{chatgpt_result}"
                    }
                }
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
