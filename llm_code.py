

#///script
# requires-python = ">3.11"
# dependencies = [
#   "pytesseract",
#   "Pillow",
#   "numpy",
#   "scikit-learn",
#
# ]
#///
import os
import subprocess
import re
import json
from datetime import datetime
from collections import defaultdict
from PIL import Image
import pytesseract
import sqlite3

# Task A1: Run the datagen.py script
user_email = os.environ.get('user.email')
subprocess.run(['python3', 'https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py', user_email])

# Task A2: Format the contents of /data/format.md using Prettier
subprocess.run(['npx', 'prettier', '--write', '/data/format.md'])

# Task A3: Count the number of Wednesdays in /data/dates.txt
DATE_FORMATS = [
    (r"^\d{2}-[A-Za-z]{3}-\d{4}$", "%d-%b-%Y"),  
    (r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$", "%Y/%m/%d %H:%M:%S"),  
    (r"^\d{4}-\d{2}-\d{2}$", "%Y-%m-%d"),  
    (r"^[A-Za-z]{3} \d{2}, \d{4}$", "%b %d, %Y"),  
]

wednesday_count = 0
with open('/data/dates.txt', 'r') as f:
    for line in f:
        line = line.strip()
        for pattern, date_format in DATE_FORMATS:
            if re.match(pattern, line):
                date = datetime.strptime(line, date_format)
                if date.weekday() == 2:  # 2 = Wednesday
                    wednesday_count += 1
                    break

with open('/data/dates-wednesdays.txt', 'w') as f:
    f.write(str(wednesday_count))

# Task A4: Sort the array of contacts in /data/contacts.json
with open('/data/contacts.json', 'r') as f:
    contacts = json.load(f)
contacts_sorted = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))
with open('/data/contacts-sorted.json', 'w') as f:
    json.dump(contacts_sorted, f, indent=2)

# Task A5: Extract the first line of the 10 most recent .log files in /data/logs/
recent_logs = sorted([os.path.join('/data/logs', f) for f in os.listdir('/data/logs') if f.endswith('.log')], key=os.path.getmtime, reverse=True)[:10]
with open('/data/logs-recent.txt', 'w') as f:
    for log in recent_logs:
        with open(log, 'r') as log_file:
            f.write(log_file.readline())

# Task A6: Extract H1 from Markdown files
index = {}
for root, dirs, files in os.walk('/data/docs/'):
    for file in files:
        if file.endswith('.md'):
            with open(os.path.join(root, file), 'r') as f:
                for line in f:
                    if line.startswith('# '):
                        index[file] = line[2:].strip()  # strip leading '# '
                        break

with open('/data/docs/index.json', 'w') as f:
    json.dump(index, f, indent=2)

# Task A7: Extract email from /data/email.txt
with open('/data/email.txt', 'r') as f:
    email_line = f.readline()
    email = re.search('<(.*?)>', email_line).group(1)

with open('/data/email-sender.txt', 'w') as f:
    f.write(email)

# Task A8: Extract credit card number from image using OCR
credit_card_image = Image.open('/data/credit-card.png')
credit_card_text = pytesseract.image_to_string(credit_card_image)
credit_card_number = re.sub(r'\D', '', credit_card_text)  # Remove all non-digit characters
with open('/data/credit-card.txt', 'w') as f:
    f.write(credit_card_number)

# Task A9: Find the most similar pair of comments
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

with open('/data/comments.txt', 'r') as f:
    comments = f.readlines()

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(comments)
cosine_similarities = cosine_similarity(X)

# Get the most similar pair
max_sim = 0
most_similar_pair = ('', '')
for i in range(len(comments)):
    for j in range(i + 1, len(comments)):
        if i != j:
            if cosine_similarities[i][j] > max_sim:
                max_sim = cosine_similarities[i][j]
                most_similar_pair = (comments[i].strip(), comments[j].strip())

with open('/data/comments-similar.txt', 'w') as f:
    f.write(f'{most_similar_pair[0]}
{most_similar_pair[1]}')

# Task A10: Calculate total sales of Gold tickets
conn = sqlite3.connect('/data/ticket-sales.db')
cursor = conn.cursor()
cursor.execute("SELECT SUM(units * price) FROM ticket_sales WHERE type = 'Gold'")
result = cursor.fetchone()[0]
with open('/data/ticket-sales-gold.txt', 'w') as f:
    f.write(str(result))

conn.close()