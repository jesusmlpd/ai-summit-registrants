"""Write a mail-merge CSV of follow-up emails, one per registrant, to emails/ (gitignored).

Usage: python3 build_emails.py path/to/WebinarRegistrationsList.csv
Each registrant is invited to join the Collective with the person who referred them.
Fill in LINKS below before sending. People who signed up twice under the same name get one email.
"""
import csv, os, sys

EXCLUDE_EMAILS = {"jesus@marblism.com"}
HOSTS = {"": "the Marblism Team", "Other": "the Marblism Team"}  # form answer -> who they join with
LINKS = {}  # host -> collective link, e.g. {"Aprille Franks": "https://..."}; missing ones stay as placeholders

def greeting_name(first):
    w = first.strip().split()[0] if first.strip() else ""
    if len(w) < 2 or not w.replace("-", "").replace("'", "").isalpha() or w.lower() == "me":
        return None
    return w.title() if w.islower() or w.isupper() else w

def email_for(p):
    host = HOSTS.get(p["ref"], p["ref"])
    short = host.split()[0] if host in p["ref"] else host  # "Aprille Franks" -> "Aprille"
    link = LINKS.get(host, "{{LINK_" + host.upper().replace("THE ", "").replace(" ", "_") + "}}")
    hi = f"Hi {p['greet']}," if p["greet"] else "Hi there,"
    invited = f" {host} invited you, and we're really glad to have you with us." if host in p["ref"] else " We're really glad to have you with us."
    subject = f"Your link to join the Collective with {short}"
    body = (f"{hi}\n\nThank you for being part of the AI Summit.{invited}\n\n"
            f"Here is your link to join the Collective with {short}:\n{link}\n\nSee you inside,\nThe Marblism Team")
    return host, subject, body

rows = {}
with open(sys.argv[1] if len(sys.argv) > 1 else ".registrations.csv", newline="", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        email = r["email"].strip().lower()
        if email in EXCLUDE_EMAILS:
            continue
        p = {"email": email, "first": r["firstName"].strip(), "last": r["lastName"].strip(),
             "greet": greeting_name(r["firstName"]), "ref": r["Who Referred You?"].strip(), "date": r["createdAt"].strip()}
        key = f"{p['first']} {p['last']}".lower()
        if key not in rows or p["date"] > rows[key]["date"]:
            rows[key] = p

os.makedirs("emails", exist_ok=True)
out = "emails/ai-summit-followups.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["email", "first_name", "last_name", "collective_with", "subject", "body"])
    for p in sorted(rows.values(), key=lambda p: (p["ref"] in HOSTS, p["ref"], p["first"].lower())):
        host, subject, body = email_for(p)
        w.writerow([p["email"], p["first"], p["last"], host, subject, body])
print(f"{len(rows)} emails written to {out}")
