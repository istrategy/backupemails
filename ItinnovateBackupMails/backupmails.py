import imaplib2
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import mysql.connector
import json
from hashlib import sha256
from datetime import datetime


def parse_date(date_str):
    try:
        date_obj = parsedate_to_datetime(date_str)
        if date_obj:
            mysql_date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            return mysql_date_str
        else:
            raise ValueError("Unable to parse date")
    except Exception as e:
        print("Error:", e)
        return None


# Function to decode email header
def decode_subject(header):
    decoded_header = decode_header(header)
    subject = decoded_header[0][0]
    charset = decoded_header[0][1]
    if charset:
        subject = subject.decode(charset)
    return subject


# Function to save email and attachments to the database
def save_email_to_database(mailbox_id, subject, sender, receiver, date, body, attachments, config):
    try:
        # Connect to MySQL
        db_connection = mysql.connector.connect(**config["database"])
        cursor = db_connection.cursor()

        # Check if the email exists in the database
        query = "SELECT id FROM emails WHERE mailbox_id = %s AND subject = %s AND sender = %s AND receiver = %s AND date = %s"
        cursor.execute(query, (mailbox_id, subject, sender, receiver, date))
        existing_email = cursor.fetchone()

        if existing_email:
            print("Email already exists in the database.")
            email_id = existing_email[0]
        else:
            # Insert the email into the database
            insert_email_query = "INSERT INTO emails (mailbox_id, subject, sender, receiver, date, body) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_email_query, (mailbox_id, subject, sender, receiver, date, body))
            email_id = cursor.lastrowid
            print("Email inserted into the database.")

            # Insert attachments into the database if they are not duplicates
            for filename, attachment_data in attachments.items():
                # Check if attachment with the same filename already exists
                cursor.execute("SELECT id FROM attachments WHERE email_id = %s AND filename = %s", (email_id, filename))
                existing_attachment = cursor.fetchone()
                if not existing_attachment:
                    # Attachment does not exist, insert it into the database
                    insert_attachment_query = "INSERT INTO attachments (email_id, filename, data) VALUES (%s, %s, %s)"
                    cursor.execute(insert_attachment_query, (email_id, filename, attachment_data))
                    print(f"Attachment '{filename}' saved in the database.")
                else:
                    print(f"Attachment '{filename}' already exists for this email, skipping.")

        db_connection.commit()
    except mysql.connector.Error as error:
        print("Error while connecting to MySQL:", error)
    finally:
        # Close MySQL connections
        if 'db_connection' in locals():
            cursor.close()
            db_connection.close()


# Load email server configuration from config file
with open("config.json") as config_file:
    config = json.load(config_file)

delete_mails = config.get("delete_mails", False)  # Get the delete_mails flag from config

# Connect to the MySQL database
try:
    db_connection = mysql.connector.connect(**config["database"])
    cursor = db_connection.cursor()

    # Retrieve records from the mailboxes table
    cursor.execute("SELECT * FROM mailboxes")
    mailboxes = cursor.fetchall()

    # Iterate through each mailbox record
    for mailbox in mailboxes:
        mailbox_id, username, email_address,  _,password, server_imap, port_imap, _, server_smtp, port_smtp, _ = mailbox

        # Connect to the IMAP server
        print(username, email_address, password, server_imap,password)
        try:
            mail        = imaplib2.IMAP4_SSL(server_imap, port_imap)
            mail.login(username, password)

            # Select the mailbox (inbox)
            mail.select("inbox")

            # Search for all emails in the inbox
            result, data = mail.search(None, "ALL")

            # Iterate through email messages
            for num in data[0].split():
                # Fetch the email message by ID
                result, message_data = mail.fetch(num, "(RFC822)")
                raw_email = message_data[0][1]

                # Parse the raw email
                msg = email.message_from_bytes(raw_email)

                # Extract email headers and content
                try:
                    subject = decode_subject(msg["subject"])
                    sender = msg["from"]
                    receiver = msg["to"]
                    date = parse_date(msg["date"])
                    if date is None:
                        print("Error: Unable to parse date", msg["date"])
                        continue  # Skip this email if date parsing fails

                    # Extract email body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if "attachment" in content_type:
                                filename = part.get_filename()
                                attachment_data = part.get_payload(decode=True)
                                attachments[filename] = attachment_data
                            elif content_type == "text/plain":
                                body = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
                    else:
                        body = msg.get_payload(decode=True).decode(msg.get_content_charset(), 'ignore')
                except Exception as e:
                    print("Error:", e)

                # Extract attachments
                attachments = {}
                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    filename = part.get_filename()
                    if filename:
                        attachment_data = part.get_payload(decode=True)
                        attachments[filename] = attachment_data

                # Calculate hash of the email content to check for duplicates
                email_content_hash = sha256(raw_email).hexdigest()

                # Save email to database if it's not a duplicate
                save_email_to_database(mailbox_id, subject, sender, receiver, date, body, attachments, config)

                # Delete the email if the delete_mails flag is true
                if delete_mails:
                    mail.store(num, '+FLAGS', '\\Deleted')
            mail.close()
            mail.logout()
        except Exception as e:
            print("Error:", e)
        # Close the connection to the IMAP server


except mysql.connector.Error as error:
    print("Error while connecting to MySQL:", error)
finally:
    # Close MySQL connections
    if 'db_connection' in locals():
        cursor.close()
        db_connection.close()
