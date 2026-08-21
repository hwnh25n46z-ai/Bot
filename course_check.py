import os
import sys
import json
import smtplib
import urllib.request
import urllib.parse
from email.mime.text import MIMEText

# --- CONFIGURATION ---
# Secrets come from GitHub Actions environment variables (set these as repo secrets).
SMS_GATEWAY = os.environ.get("4439466839@txt.att.net")          # e.g. "1234567890@txt.att.net"
GMAIL_USER = os.environ.get("skitzwasatakenusername@gmail.com")            # e.g. "yourbot@gmail.com"
GMAIL_APP_PASSWORD = os.environ.get("wttf bkuz zckz hqag")  # 16-char Gmail App Password, NOT your normal password

ROSTER = "FA26"

# component -> which section type to watch ("LAB" or "LEC")
COURSES = [
    {"subject": "ECE", "number": "2100", "watch": "LAB", "label": "ECE 2100 (LAB)"},
    {"subject": "ECE", "number": "2300", "watch": "LEC", "label": "ECE 2300 (LEC)"},
    {"subject": "PHYS", "number": "2213", "watch": "LEC", "label": "PHYS 2213 (LEC)"},
]

API_URL = "https://classes.cornell.edu/api/2.0/search/classes.json"


def send_text(message):
    """Send an SMS via email-to-text gateway, using a real authenticated SMTP server."""
    if not (SMS_GATEWAY and GMAIL_USER and GMAIL_APP_PASSWORD):
        print("Missing SMS_GATEWAY / GMAIL_USER / GMAIL_APP_PASSWORD env vars — cannot send text.")
        return
    try:
        msg = MIMEText(message)
        msg["To"] = SMS_GATEWAY
        msg["From"] = GMAIL_USER
        msg["Subject"] = "Course Alert"

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, [SMS_GATEWAY], msg.as_string())
        print(f"Text alert sent: {message}")
    except Exception as e:
        print(f"Failed to send text: {e}")


def fetch_subject_json(subject):
    """Call Cornell's real Class Roster API (JSON), not the HTML page."""
    params = {"roster": ROSTER, "subject": subject}
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def section_is_open(section):
    """
    Handle a couple of possible field shapes defensively, since Cornell's API
    has changed field names across versions (openStatus / enrlStat / openStatusText).
    Run once with a plain print(section) if this stops matching — the API can
    change without notice.
    """
    if "openStatus" in section:
        return bool(section["openStatus"])
    if "enrlStat" in section:
        return str(section["enrlStat"]).upper() == "O"
    if "openStatusText" in section:
        return str(section["openStatusText"]).strip().lower() == "open"
    return False


def check_course(course):
    try:
        data = fetch_subject_json(course["subject"])
    except Exception as e:
        print(f"Error fetching {course['subject']}: {e}")
        return

    classes = data.get("data", {}).get("classes", [])
    target_course = f"{course['subject']} {course['number']}"

    for cls in classes:
        catalog_nbr = str(cls.get("catalogNbr", "")).strip()
        if catalog_nbr != course["number"]:
            continue

        for group in cls.get("enrollGroups", []):
            for section in group.get("classSections", []):
                component = section.get("ssrComponent", "")  # e.g. "LEC", "LAB", "DIS"
                if component != course["watch"]:
                    continue
                if section_is_open(section):
                    send_text(f"ALERT: {course['watch']} section is OPEN for {course['label']}!")
                    print(f"OPEN: {target_course} section {section.get('section', '?')}")
                    return  # one alert per run is enough

    print(f"{target_course}: no open {course['watch']} section found this check.")


def main():
    for course in COURSES:
        check_course(course)


if __name__ == "__main__":
    main()
