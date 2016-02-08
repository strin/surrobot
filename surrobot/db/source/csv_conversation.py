# -*- coding: utf_8 -*-
# extract email from csv conversation format
# header: id	email_id	thread_id	date	original_email	normalised_email	email_words	response_subject	response_email	created_at	updated_at	user_id	user_email_id
import csv

from surrobot.db.db import Email, EmailDB

def extract(csv_path):
    '''
    extract eamil from csv file.

    Return
    ======
    list of pairs (in_mail, out_mail)
    '''
    sanitize_text = lambda body: body.decode('unicode_escape').encode('ascii', 'ignore') # TODO: support unicode.

    with open(csv_path, 'rU') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # create mails in inbox.
            in_mail = Email(
                        email_addr=row['user_email_id'],
                        sent_at=None,
                        message_id=row['email_id'],
                        thread_id=row['thread_id'],
                        subject='',
                        headers='',
                        body=sanitize_text(row['normalised_email'])
                    )
            # create response mail
            out_mail = Email(
                        email_addr='',
                        sent_at=None,
                        message_id=row['email_id'],
                        thread_id=row['thread_id'],
                        subject='',
                        headers='',
                        body=sanitize_text(row['response_email'])
                    )
            yield (in_mail, out_mail)


def sync(csv_path):
    inbox_db = EmailDB('inbox')
    outbox_db = EmailDB('outbox')

    in_mails = []
    out_mails = []
    for (in_mail, out_mail) in extract(csv_path):
        in_mails.append(in_mail)
        out_mails.append(out_mail)

    def get_in_mail():
        for (mi, in_mail) in enumerate(in_mails):
            print '[inbox][%d/%d]' % (mi, len(in_mails))
            yield in_mail

    def get_out_mail():
        for (mi, out_mail) in enumerate(out_mails):
            print '[outbox][%d/%d]' % (mi, len(out_mails))
            yield out_mail

    inbox_db.update_all('csv@evolutics.com', get_in_mail())
    outbox_db.update_all('csv@evolutics.com', get_out_mail())

if __name__ == '__main__':
    sync('data/conversations.csv')


