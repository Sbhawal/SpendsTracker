import sqlite3
from app.Constants import *
from app.google_apis import *


def connectToDB():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    return conn, cursor

def initializeDB():
    # Connect to the database (or create one if it doesn't exist)
    conn, cursor = connectToDB()
    # Create the table with the specified columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            ID TEXT PRIMARY KEY,
            THREAD_ID TEXT,
            DATE TEXT,
            SENDER TEXT,
            SUBJECT TEXT,
            BODY TEXT,
            ATTACHMENT TEXT,
            LABEL TEXT
        )
    ''')
    # Commit changes and close the connection
    conn.commit()
    conn.close()

def add_Entry_in_DB(ID,THREAD_ID,DATE,BODY,SUBJECT,SENDER,ATTACHMENT,LABEL):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO emails (ID,THREAD_ID,DATE,BODY,SUBJECT,SENDER,ATTACHMENT,LABEL)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (ID,THREAD_ID,DATE,BODY,SUBJECT,SENDER,ATTACHMENT,LABEL))
    conn.commit()
    conn.close()

def update_DB_On_Single_Date(from_date, to_date):
    messages = get_email_messages(from_date, to_date, service=service, max_results=100)
    for message in tqdm(messages):
        details = get_email_message_details(service, message['id'])
        if details:
            ID = message['id']
            THREAD_ID = message['threadId']
            DATE = details['date']
            BODY = details['body']
            SUBJECT = details['subject']
            SENDER = details['sender']
            ATTACHMENT = details['has_attachments']
            LABEL = details['label']
            add_Entry_in_DB(ID,THREAD_ID,DATE,BODY,SUBJECT,SENDER,ATTACHMENT,LABEL)


def get_rows_from_DB():
    conn, cursor = connectToDB()
    cursor.execute('SELECT * FROM emails')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()            


initializeDB()