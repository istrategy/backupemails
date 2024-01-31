# BACKUP EMAILS
### Rational
This project was created to free up space on my hosting account. The account did not offer a way to 
download mailboxes and I wanted to archive emails it for future reference.

### How it works
The mailboxes are defined in the mailboxes table (See below).
Just run the _backupmails.py_ python script in your compiler (I recommend PyCharm).   
It will run through all your mailboxes and store the mail information in the emails table and the attachments in the attachments table.  
  
To view an attachment use the *download_file_from_database(attachment_id)* function in the _downloadfile.py_ file.


#### Example mailbox record
id, name, email_address, username, password, incoming_server, imap_port, pop3_port, outgoing_server, smtp_port, deletemails, skipaccount
1,accountname,mail@mail.com,mail@mail.com,mailboxpassword,mailserverurl,993,995,outgoingmailserver,465,0,0


### Technical Details
The project was created in __Python 3.11__  
It uses a __MySql__ server in a __Docker__ container.  
The database connection parameters must be put in the _config.json_ file.  
A example config file is included as _example_config.json_.  
There is also a _requirements.txt_ file.
To use the _downloadfile.py_ script to view email attachments one must set up the "download_directory" in the _config.json_ file.

### Future improvements
There are a few encoding issues with some of the mail headers. The scripts deletes the mails if the mailbox.deletemails is set.
# Contact Details
This script was created by 

__Gert van Eeden__  
info@itinnovate.co.za  
https://itinnovate.co.za  
https://www.linkedin.com/in/gertvaneeden/

Contact me if you have a similar requirements or if you want to suggest further improvements.  
You can also download and modify the script for your own requirements.


