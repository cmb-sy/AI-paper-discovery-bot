import logging
import json
from openai import OpenAI

def process_paper_with_chatgpt(paper, api_key, model="gpt-3.5-turbo", temperature=0.7):        
    try:
        client = OpenAI(api_key=api_key)
        
        # 論文情報を整形
        authors = ", ".join(author.name for author in paper.authors)
        title = ' '.join(paper.title.split())  # 不要な改行を削除
        abstract = ' '.join(paper.summary.split())  # 不要な改行を削除
        
        prompt = f"""
以下の論文を日本語で要約し、その重要性と新規性を簡潔に説明してください。また、この論文がどのような応用や発展性を持つか短く述べてください：

タイトル: {title}
アブストラクト:
{abstract}

以下のJSON形式で回答してください：
```json
{{
  "summary": "論文の要約（日本語・300文字程度）",
  "importance": "論文の重要性（日本語・200文字程度）",
  "applications": "可能性のある応用や発展性（日本語・200文字程度）"
}}
```
JSONのみを返してください。他の説明は不要です。
"""
        # API呼び出し
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "あなたは学術論文を分析するAIアシスタントです。最新の研究論文を簡潔に要約し、その重要性を説明します。"},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        
        # レスポンスから必要な情報を抽出
        response_text = completion.choices[0].message.content.strip()
        
        # JSON部分を抽出
        json_match = response_text
        if "```json" in response_text:
            json_match = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_match = response_text.split("```")[1].strip()
            
        # JSONをパース
        result = json.loads(json_match)
        return result
        
    except Exception as e:
        return None
