import os
import re
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

def check_bachelor_grade(pdf_path: str) -> tuple[bool, tuple[str, str]]:
    """Liest die PDF aus und prüft, ob bei der Bachelorarbeit/Kolloquium eine Note/ein Status eingetragen ist."""
    if not os.path.exists(pdf_path):
        return False, ("Keine Note gefunden", "PDF-Datei nicht gefunden.")

    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""

    lines = full_text.splitlines()
    relevant_lines = []

    # Nur Zeilen filtern, die die Bachelorarbeit betreffen
    for line in lines:
        if any(keyword in line.lower() for keyword in ["bachelor-arbeit"]):
            relevant_lines.append(line.strip())

    if not relevant_lines:
        return False, ("Keine Note gefunden", "Keine Zeile zur Bachelorarbeit in der PDF gefunden.")

    print(f"Gefundene Zeilen zur Bachelorarbeit:\n" + "\n".join(relevant_lines))

    found_entries = []
    
    # 1. Noten-Muster: z.B. 1,0 bis 5,0
    grade_pattern = re.compile(r"\b[1-5],[0-9]\b")
    
    # 2. Status-Muster: nur als eigenständige Wörter (verhindert False-Positives in "Arbeit")
    status_pattern = re.compile(r"\b(bestanden|nicht bestanden|be|nb)\b", re.IGNORECASE)

    for line in relevant_lines:
        has_grade = bool(grade_pattern.search(line))
        has_status = bool(status_pattern.search(line))

        if has_grade or has_status:
            print(f"Treffer in Zeile: {line}")
            grade = grade_pattern.search(line).group(0)
            print(f"Gefundene Note: {grade}")
            found_entries.append(line)

    if found_entries:
        details = "\n".join(found_entries)
        return True, (grade, f"Bachelorarbeits-Ergebnis eingetragen!\n\nDetails:\n{details}")

    return False, ("Keine Note gefunden", "Bachelorarbeit gefunden (Status: angemeldet / ZU), aber noch keine Note eingetragen.")


def send_email(recipient: str, subject: str, body: str, attachment_path: str = None):
    """Versendet eine E-Mail mit optionalem PDF-Anhang."""
    username = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")  # Bei Gmail: App-Passwort verwenden!

    message = MIMEMultipart()
    message["From"] = username
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # PDF anhängen
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
            pdf_attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.basename(attachment_path),
            )
            message.attach(pdf_attachment)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(username, recipient, message.as_string())
        print("E-Mail erfolgreich gesendet!")
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")


# ==========================================
# Ablaufsteuerung
# ==========================================
if __name__ == "__main__":
    PDF_FILE = "Leistungsuebersicht.pdf"
    RECIPIENT_EMAIL = "maltenoack590@gmail.com" # oder deine Ziel-Adresse

    is_graded, (grade, info_text) = check_bachelor_grade(PDF_FILE)
    print(info_text)

    if is_graded:
        print("Sende Benachrichtigung per E-Mail...")
        send_email(
            recipient=RECIPIENT_EMAIL,
            subject=f"🎓 Note für Bachelorarbeit eingetragen {grade}!",
            body=f"Hallo,\n\nin deiner Leistungsübersicht hat sich etwas getan:\n\n{info_text}\n\nDie aktuelle PDF ist im Anhang.",
            attachment_path=PDF_FILE,
        )
    else:
        print("Noch kein neuer Eintrag – keine E-Mail nötig.")
        # Lösche die PDF-Datei, um Speicherplatz zu sparen
        if os.path.exists(PDF_FILE):
            os.remove(PDF_FILE)
            print(f"Alte PDF-Datei '{PDF_FILE}' gelöscht.")