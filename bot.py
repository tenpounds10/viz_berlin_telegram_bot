import os
import feedparser
import requests

RSS_URL = "https://bsky.app/profile/did:plc:n3hodnajzex6mjxkrvd2pqpt/rss"
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
LAST_SEEN_FILE = "last_seen.txt"


def load_last_seen() -> str:
    if os.path.exists(LAST_SEEN_FILE):
        with open(LAST_SEEN_FILE, "r") as f:
            return f.read().strip()
    return ""


def save_last_seen(entry_id: str):
    with open(LAST_SEEN_FILE, "w") as f:
        f.write(entry_id)


def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()


def main():
    feed = feedparser.parse(RSS_URL)
    entries = feed.entries

    if not entries:
        print("No entries found in feed.")
        return

    last_seen = load_last_seen()
    new_entries = []

    for entry in entries:
        entry_id = entry.get("id", entry.get("link", ""))
        if entry_id == last_seen:
            break
        new_entries.append(entry)

    if not new_entries:
        print("No new entries.")
        return

    # Send oldest first
    for entry in reversed(new_entries):
        title = entry.get("title", "New post")
        link = entry.get("link", "")
        summary = entry.get("summary", "")

        # Clean up summary if it's just a repeat of the title
        if summary and summary.strip() != title.strip():
            message = f"{summary}\n\n<a href='{link}'> Open post</a>"
        else:
            message = f"<a href='{link}'> {title}</a>"

        send_telegram(message)
        print(f"Sent: {link}")

    # Save the most recent entry's ID
    newest_id = entries[0].get("id", entries[0].get("link", ""))
    save_last_seen(newest_id)
    print(f"Updated last_seen to: {newest_id}")


if __name__ == "__main__":
    main()
