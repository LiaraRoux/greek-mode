
import sqlite3
import xml.etree.ElementTree as ET

# Paths
greek_xml_path = "data/greek.xml"
english_xml_path = "data/english.xml"
db_path = "database/iliad.db"

NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

# Create DB and table
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS iliad_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book INTEGER NOT NULL,
    line INTEGER NOT NULL,
    greek TEXT,
    english TEXT,
    source TEXT
);
''')

# Parse Greek
greek_lines = {}
greek_tree = ET.parse(greek_xml_path)
for div in greek_tree.findall('.//tei:div[@type="textpart"]', NS):
    if 'n' not in div.attrib:
        continue
    try:
        book_n = int(div.attrib['n'])
    except ValueError:
        continue
    for l in div.findall('.//tei:l', NS):
        if 'n' not in l.attrib:
            continue
        try:
            line_n = int(l.attrib['n'])
        except ValueError:
            continue
        greek_lines[(book_n, line_n)] = l.text.strip() if l.text else ''

# Parse English
english_lines = {}
english_tree = ET.parse(english_xml_path)
for div in english_tree.findall('.//tei:div[@type="textpart"]', NS):
    if 'n' not in div.attrib:
        continue
    try:
        book_n = int(div.attrib['n'])
    except ValueError:
        continue
    for l in div.findall('.//tei:l', NS):
        if 'n' not in l.attrib:
            continue
        try:
            line_n = int(l.attrib['n'])
        except ValueError:
            continue
        english_lines[(book_n, line_n)] = l.text.strip() if l.text else ''

# Insert aligned lines
for key in sorted(set(greek_lines) | set(english_lines)):
    book, line = key
    greek = greek_lines.get(key)
    english = english_lines.get(key)

    cursor.execute('SELECT id FROM iliad_lines WHERE book=? AND line=?', (book, line))
    row = cursor.fetchone()

    if row:
        cursor.execute('UPDATE iliad_lines SET english=?, source=? WHERE id=?', (english, 'Pope', row[0]))
    else:
        cursor.execute('''
            INSERT INTO iliad_lines (book, line, greek, english, source)
            VALUES (?, ?, ?, ?, ?)
        ''', (book, line, greek, english, 'Pope' if english else 'Perseus'))

conn.commit()
conn.close()
