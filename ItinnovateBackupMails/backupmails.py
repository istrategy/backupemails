import imaplib2
from email.header import decode_header
import email
import mysql.connector

# Function to decode email header
def decode_subject(header):
    decoded_header = decode_header(header)
    subject = decoded_header[0][0]
    charset = decoded_header[0][1]
    if charset:
        subject = subject.decode(charset)
    return subject

# Connect to MySQL
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="itinnovate@199",
    database="mailboxes",
    port=3100
)
cursor = db_connection.cursor()

# Query mailboxes information
query = "SELECT id, email_address, username, password, incoming_server, imap_port FROM mailboxes"
cursor.execute(query)
mailboxes = cursor.fetchall()

# Iterate through mailboxes
for mailbox in mailboxes:
    mailbox_id, email_address, username, password, incoming_server, imap_port = mailbox

    # Connect to the IMAP server
    mail = imaplib2.IMAP4_SSL(incoming_server, imap_port)
    mail.login(username, password)

    # Select the mailbox (inbox)
    mail.select("inbox")

    # Search for all emails in the inbox
    result, data = mail.search(None, "ALL")

    # Iterate through email headers
    for num in data[0].split():
        # Fetch the email header by ID
        result, header_data = mail.fetch(num, "(BODY[HEADER])")
        raw_header = header_data[0][1]

        # Parse the raw email header
        msg = email.message_from_bytes(raw_header)

        # Extract email subject
        subject = decode_subject(msg["subject"])

        print(f"Mailbox ID: {mailbox_id}, Email Address: {email_address}")
        print(f"Subject: {subject}")

    # Close the connection to the IMAP server
    mail.close()

# Close MySQL connections
cursor.close()
db_connection.close()
