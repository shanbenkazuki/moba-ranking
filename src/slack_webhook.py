import requests

def send_slack_notification(webhook_url: str, message: str) -> bool:
    """
    SlackのWebhook URLを使ってメッセージを送信する

    Args:
        webhook_url (str): SlackのWebhook URL
        message (str): 送信するテキストメッセージ

    Returns:
        bool: 送信成功時はTrue、失敗時はFalse
    """
    payload = {"text": message}
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Slack通知の送信に失敗しました: {e}")
        return False
