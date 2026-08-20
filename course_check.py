import time
import smtplib
import urllib.request
from email.mime.text import MIMEText

# --- CONFIGURATION (CHANGE THESE) ---
# Your SMS gateway address MUST have quotes around it
SMS_GATEWAY = "4439466839@txt.att.net" 

# Course 1: Checking specifically for LABS
URL_COURSE_1 = "https://classes.cornell.edu/browse/roster/FA26/class/ECE/2100"
NAME_COURSE_1 = "ECE 2100 (LAB)"

# Course 2: Checking specifically for LECTURES
URL_COURSE_2 = "https://classes.cornell.edu/browse/roster/FA26/class/ECE/2300"
NAME_COURSE_2 = "ECE 2300 (LEC)"

# Course 3: Checking specifically for LECTURES
URL_COURSE_3 = "https://classes.cornell.edu/browse/roster/FA26/class/PHYS/2213"
NAME_COURSE_3 = "PHYS 2213 (LEC)"
# -------------------------------------

def send_text(message):
    try:
        msg = MIMEText(message)
        msg['To'] = SMS_GATEWAY
        msg['From'] = "cornellbot@pythonanywhere.com"
        server = smtplib.SMTP('localhost')
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        server.quit()
        print(f"Text alert sent: {message}")
    except Exception as e:
        print(f"Failed to send text: {e}")

def fetch_html(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (iPhone)'})
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

print("Multi-Course Monitor started. Checking every 60 seconds...")

while True:
    try:
        # --- CHECK COURSE 1 (LABS ONLY) ---
        html1 = fetch_html(URL_COURSE_1)
        sections = html1.split('<div class="class-section')
        lab_is_open = False
        for section in sections:
            if "LAB" in section and "status-open" in section:
                lab_is_open = True
                break
        if lab_is_open:
            send_text(f"ALERT: A LAB section is OPEN for {NAME_COURSE_1}!")

        # --- CHECK COURSE 2 (LECTURES ONLY) ---
        html2 = fetch_html(URL_COURSE_2)
        sections = html2.split('<div class="class-section')
        lec2_is_open = False
        for section in sections:
            if ("LEC" in section or "Lecture" in section) and "status-open" in section:
                lec2_is_open = True
                break
        if lec2_is_open:
            send_text(f"ALERT: The LECTURE is OPEN for {NAME_COURSE_2}!")

        # --- CHECK COURSE 3 (LECTURES ONLY) ---
        html3 = fetch_html(URL_COURSE_3)
        sections = html3.split('<div class="class-section')
        lec3_is_open = False
        for section in sections:
            if ("LEC" in section or "Lecture" in section) and "status-open" in section:
                lec3_is_open = True
                break
        if lec3_is_open:
            send_text(f"ALERT: The LECTURE is OPEN for {NAME_COURSE_3}!")

        print("Scan complete. All targeted sections still closed. Waiting 60 seconds...")

    except Exception as e:
        print(f"Error scanning roster: {e}")
        
    time.sleep(60)
        # Add these lines at the very bottom inside the while loop:
