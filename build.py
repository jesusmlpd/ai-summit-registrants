"""Embed registrant data into index.html from the webinar CSV export.

Usage: python3 build.py path/to/WebinarRegistrationsList.csv
Only names, referrer and signup date are published. Emails and phones never leave this machine.
"""
import csv, json, re, sys, datetime

EXCLUDE_EMAILS = {"jesus@marblism.com"}  # internal test signups
RENAME = {"Other": "Marblism Team (Mateo, Lake, Malo)"}  # "Other" in the form means our own team

src = sys.argv[1] if len(sys.argv) > 1 else ".registrations.csv"
people = []
with open(src, newline="", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        email = r["email"].strip().lower()
        if email in EXCLUDE_EMAILS or r["status"].strip() != "registered":
            continue
        first, last = r["firstName"].strip(), r["lastName"].strip()
        name = " ".join(w if not w.isupper() or len(w) < 3 else w.title() for w in f"{first} {last}".split() if "@" not in w) or "Name withheld"
        people.append({
            "name": name,
            "ref": RENAME.get(r["Who Referred You?"].strip(), r["Who Referred You?"].strip()) or "Not specified",
            "date": r["createdAt"].strip()[:10],
        })

data = {"updated": datetime.date.today().isoformat(), "people": people}
html = open("index.html", encoding="utf-8").read()
payload = "window.REG_DATA = " + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + ";"
html = re.sub(r'(<script id="reg-data">).*?(</script>)', lambda m: m.group(1) + payload + m.group(2), html, flags=re.S)
open("index.html", "w", encoding="utf-8").write(html)
print(f"{len(people)} registrants embedded in index.html")
