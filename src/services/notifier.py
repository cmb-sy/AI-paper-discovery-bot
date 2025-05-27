import os
import json
from src.api.slack import send_slack_notification
from src.utils.logger import get_logger

logger = get_logger()

def notify_selected_papers(selected_papers):
    if not selected_papers:
        logger.info("No papers to notify.")
        return

    message = "選別された論文:\n"
    for paper in selected_papers:
        message += f"- {paper['title']} by {', '.join(paper['authors'])}\n"

    try:
        send_slack_notification(message)
        logger.info("Notification sent to Slack.")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")