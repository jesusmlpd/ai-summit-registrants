"""Write a mail-merge CSV of follow-up emails, one per registrant, to emails/ (gitignored).

Usage: python3 build_emails.py path/to/WebinarRegistrationsList.csv [collective_link]
People who signed up twice under the same name get one email (attended/most recent wins).
"""
import csv, os, sys

EXCLUDE_EMAILS = {"jesus@marblism.com"}
ATTENDED = {"live", "on-demand"}
TEAM = {"", "Other"}  # Marblism team signups and blank answers get no referrer line
LINK = sys.argv[2] if len(sys.argv) > 2 else "{{COLLECTIVE_LINK}}"

def greeting_name(first):
    w = first.strip().split()[0] if first.strip() else ""
    if len(w) < 2 or not w.replace("-", "").replace("'", "").isalpha() or w.lower() == "me":
        return None
    return w.title() if w.islower() or w.isupper() else w

def email_for(p):
    hi = f"Hi {p['greet']}," if p["greet"] else "Hi there,"
    ref = p["ref"] if p["ref"] not in TEAM else None
    if p["attended"]:
        subject = "Thank you for joining the AI Summit"
        intro = "Thank you for joining the AI Summit."
        if ref:
            intro += f" {ref} invited you, and we're really glad you made it."
    else:
        subject = "Your link to join the Collective"
        intro = "Thank you for registering for the AI Summit."
        if ref:
            intro += f" {ref} invited you, and we saved you a spot."
        intro += " We missed you live, but you can still be part of what comes next."
    body = f"{hi}\n\n{intro}\n\nHere is your link to join the Collective:\n{LINK}\n\nSee you inside,\nThe Marblism Team"
    return subject, body

rows = {}
with open(sys.argv[1] if len(sys.argv) > 1 else ".registrations.csv", newline="", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        email = r["email"].strip().lower()
        if email in EXCLUDE_EMAILS:
            continue
        p = {"email": email, "first": r["firstName"].strip(), "last": r["lastName"].strip(),
             "greet": greeting_name(r["firstName"]), "ref": r["Who Referred You?"].strip(),
             "attended": r["status"].strip() in ATTENDED, "date": r["createdAt"].strip()}
        key = f"{p['first']} {p['last']}".lower()
        old = rows.get(key)
        if old is None or (p["attended"], p["date"]) > (old["attended"], old["date"]):
            rows[key] = p

os.makedirs("emails", exist_ok=True)
out = "emails/ai-summit-followups.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["email", "first_name", "last_name", "referred_by", "attended", "subject", "body"])
    for p in sorted(rows.values(), key=lambda p: (p["ref"] in TEAM, p["ref"], p["first"].lower())):
        subject, body = email_for(p)
        w.writerow([p["email"], p["first"], p["last"], p["ref"] or "Not specified",
                    "yes" if p["attended"] else "no", subject, body])
print(f"{len(rows)} emails written to {out}")
