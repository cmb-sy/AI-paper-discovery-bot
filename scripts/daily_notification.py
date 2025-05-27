import os
import schedule
import time
from src.services.paper_selector import select_papers
from src.services.translator import translate_summary
from src.services.notifier import send_notification

def daily_notification():
    papers = select_papers()
    for paper in papers:
        translated_summary = translate_summary(paper.summary)
        message = f"タイトル: {paper.title}\n著者: {paper.authors}\n要約: {translated_summary}"
        send_notification(message)

if __name__ == "__main__":
    schedule.every().day.at("09:00").do(daily_notification)  # 毎日09:00に通知を実行

    while True:
        schedule.run_pending()
        time.sleep(60)  # 1分ごとにスケジュールを確認