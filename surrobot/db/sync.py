# -*- coding: utf_8 -*-
from sys import stderr
import simplejson as json

from surrobot.config import EMAIL_DB_FILE_NAME
from surrobot.db.db import sql, DBConn


class EmailDBConn(DBConn):
    def __enter__(self):
        conn = sql.connect(EMAIL_DB_FILE_NAME)
        conn.row_factory = sql.Row
        # manages access tokens for user's email account.
        conn.execute("""CREATE TABLE IF NOT EXISTS email
                    (email text,
                    message_id text,
                    thread_id text,
                    date text,
                    header text,
                    subject text,
                    body text)""")
        conn.commit()
        self.conn = conn
        return conn

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()


class EmailDB(object):
    '''
    manages the interface with db to save emails.
    '''
    @staticmethod
    def update_all(email_addr, emails):
        with EmailDBConn() as conn:
            cursor = conn.cursor()
            for email in emails:
                try:
                    email_data = {
                            'email_addr': email_addr,
                            'message_id': email.message_id,
                            'thread_id': email.thread_id,
                            'date': '' if not email.sent_at else email.sent_at.isoformat(),
                            'header': json.dumps(email.headers),
                            'subject': email.subject,
                            'body': '' if not email.body else email.body.decode('unicode_escape').encode('ascii','ignore')
                        }

                    if not email.message_id:
                        continue

                    # print email_data
                    email_data = {key: unicode(val) for (key, val) in email_data.items()}
                    # update database.
                    if EmailDB.get_message(email_addr, email.message_id):
                        cursor.execute('''
                                UPDATE email
                                SET
                                    thread_id=:thread_id,
                                    date=:date,
                                    header=:header,
                                    subject=:subject,
                                    body=:body
                                WHERE message_id=:message_id
                                AND email=:email_addr''', email_data)
                    else:
                        cursor.execute('''
                                INSERT INTO email
                                (email, message_id,
                                thread_id, date, header, subject, body)
                                VALUES
                                (:email_addr, :message_id,
                                :thread_id, :date, :header, :subject, :body
                                )''', email_data)
                    conn.commit()
                except Exception as e:
                    print>>stderr, '[error in store]', e.message


    @staticmethod
    def get_message(email_addr, message_id):
        with EmailDBConn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                    SELECT * FROM email WHERE email=:email AND message_id=:message_id
                    ''', dict(email=email_addr, message_id=message_id))
            row = cursor.fetchone()
            if row:
                return {
                    key: row[key] for key in row.keys()
                }
            else:
                return None

    def enumerate(email_addr):
        pass


def sync(email_addr):
    try:
        from surrobot.db.source.gmail_source import extract, access_token, AccessToken
        messages = extract(
                email_addr=email_addr,
                access_token=AccessToken.get(email_addr),
                domain='all_mail')

        def fetch_messages():
            for (mi, message) in enumerate(messages):
                try:
                    message.fetch()
                    print '[%d]' % mi, message.subject
                    yield message
                except Exception as e:
                    print>>stderr, '[error in fetch]', e.message


        EmailDB.update_all(email_addr, fetch_messages())

    except ImportError as e:
        print>>stderr, 'sync: cannot sync with gmail'
        print>>stderr, e.message


if __name__ == '__main__':
    sync('stl501@gmail.com')


