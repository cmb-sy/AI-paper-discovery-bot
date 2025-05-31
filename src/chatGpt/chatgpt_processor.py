"""
ChatGPTによる論文処理を行うモジュール
"""
import os
from src.config_loader import get_config
from src.utils import print_with_timestamp

def process_paper_with_chatgpt(paper):
    """論文をChatGPT APIで処理する"""
    config = get_config()
    
    # ChatGPT設定の取得
    use_chatgpt = config.get('chatgpt', {}).get('use_chatgpt', False)
    api_key = config.get('chatgpt', {}).get('api_key', os.environ.get('OPENAI_API_KEY', ''))
    model = config.get('chatgpt', {}).get('model', 'gpt-3.5-turbo')
    temperature = config.get('chatgpt', {}).get('temperature', 0.7)
    
    if not use_chatgpt or not api_key:
        return paper
        
    try:
        from .chatgpt_utils import process_paper_with_chatgpt as chatgpt_process
        print_with_timestamp("ChatGPT APIを使用して論文を処理しています...")
        
        chatgpt_result = chatgpt_process(
            paper,
            api_key,
            model=model,
            temperature=temperature
        )
        paper.chatgpt_result = chatgpt_result
        
        return paper
    except ImportError:
        print_with_timestamp("ChatGPTユーティリティをインポートできませんでした。ChatGPTモードは無効になります。")
        return paper
    except Exception as e:
        print_with_timestamp(f"ChatGPTによる処理中にエラーが発生しました: {e}")
        return paper
