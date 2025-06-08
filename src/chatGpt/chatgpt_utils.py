from openai import OpenAI

def process_paper_with_chatgpt(paper, api_key, model="gpt-3.5-turbo", temperature=0.7):        
    try:
        client = OpenAI(api_key=api_key)
        # 論文情報を整形
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
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "あなたは学術論文を読んで分析と整理をし、わかりやすく要点を教えてくれるアシスタントです"},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        
        # レスポンスから必要な情報を抽出
        response_text = completion.choices[0].message.content.strip()
        
        return response_text
        
    except Exception as e:
        return None
