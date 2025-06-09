"""
論文情報のフォーマットを行うモジュール
"""
from .config_loader import get_config
from .utils import print_with_timestamp

def clean_text(text):
    """テキストから不要な空白を削除します"""
    return ' '.join(text.split())

def format_paper_for_slack(paper):
    """論文情報をSlack用のブロック形式にフォーマットします"""
    config = get_config()
    llm_provider = config.get('llm', {}).get('provider', 'none')
    
    try:
        title = clean_text(paper.title)
        summary = clean_text(paper.summary)
        
        # ヘッダーブロック
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title,
                    "emoji": True
                }
            },
        ]
        
        # LLM処理結果の追加
        llm_result = None
        llm_name = ""
        
        if llm_provider == "gemini":
            llm_result = getattr(paper, 'gemini_result', None)
            llm_name = "Gemini"
        elif llm_provider == "chatgpt":
            llm_result = getattr(paper, 'chatgpt_result', None)
            llm_name = "ChatGPT"
        
        # コンテンツブロックの追加
        if llm_provider != "none" and llm_result:
            if llm_result.startswith("※"):
                # LLMエラーの場合
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
                            "text": f"*元の概要:*\n{summary}"
                        }
                    }
                ])
            else:
                # LLM要約の場合
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{llm_name}による要約:*\n{llm_result}"
                    }
                })
        else:
            # LLMを使用しない、または結果がない場合
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*概要:*\n{summary}"
                }
            })
        
        # フッターブロック
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
        
        return {"blocks": blocks}
        
    except Exception as e:
        print_with_timestamp(f"論文のフォーマット中にエラーが発生しました: {e}")
        return None
