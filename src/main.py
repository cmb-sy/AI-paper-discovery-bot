import schedule
import time
from api.arxiv import fetch_papers
from services.paper_selector import select_papers
from services.translator import translate_summary
from services.notifier import send_notification

def job():
    papers = fetch_papers()
    selected_papers = select_papers(papers)
    
    for paper in selected_papers:
        translated_summary = translate_summary(paper.summary)
        send_notification(paper.title, paper.authors, translated_summary)

if __name__ == "__main__":
    schedule.every().day.at("09:00").do(job)  # 毎日09:00にジョブを実行

    while True:
        schedule.run_pending()
        time.sleep(1)