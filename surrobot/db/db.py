# shared database utils.
import sqlite3 as sql
import simplejson as json
import sys

from surrobot.config import EMAIL_DB_FILE_NAME


class DBConn(object):
    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self, type, value, traceback):
        raise NotImplementedError()


class Email(object):
    def __init__(self, email_addr, message_id, thread_id, sent_at, subject, headers, body):
        self.email_addr = email_addr
        self.message_id = message_id
        self.thread_id = thread_id
        self.sent_at = sent_at
        self.subject = subject
        self.headers = headers
        self.body = body

    def __repr__(self):
        return '\t'.join(['[%s]' % self.message_id, self.body])


class EmailDBConn(DBConn):
    def __init__(self, db=EMAIL_DB_FILE_NAME):
        self.db = db

    def __enter__(self):
        conn = sql.connect(self.db)
        conn.row_factory = sql.Row
        # manages access tokens for user's email account.
        conn.execute("""CREATE TABLE IF NOT EXISTS outbox
                    (email text,
                    message_id text,
                    thread_id text,
                    date text,
                    header text,
                    subject text,
                    body text)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS inbox
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
    def __init__(self, table, db=EMAIL_DB_FILE_NAME):
        self.db = db
        self.table = table


    def update_all(self, email_addr, emails):
        with EmailDBConn(self.db) as conn:
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
                    if self.get_message(email_addr, email.message_id):
                        cursor.execute('''
                                UPDATE %s
                                SET
                                    thread_id=:thread_id,
                                    date=:date,
                                    header=:header,
                                    subject=:subject,
                                    body=:body
                                WHERE message_id=:message_id
                                AND email=:email_addr''' % self.table, email_data)
                    else:
                        cursor.execute('''
                                INSERT INTO %s
                                (email, message_id,
                                thread_id, date, header, subject, body)
                                VALUES
                                (:email_addr, :message_id,
                                :thread_id, :date, :header, :subject, :body
                                )''' % self.table, email_data)
                    conn.commit()
                except Exception as e:
                    print>>sys.stderr, '[error in store]', e.message


    def get_message(self, email_addr, message_id):
        with EmailDBConn(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                    SELECT * FROM %s WHERE email=:email AND message_id=:message_id
                    ''' % self.table, dict(email=email_addr, message_id=message_id))
            row = cursor.fetchone()
            if row:
                return {
                    key: row[key] for key in row.keys()
                }
            else:
                return None

    def select(self, where='', data={}):
        if where:
            where = 'WHERE ' + where
        with EmailDBConn(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT * from %s %s'''
                    % (self.table, where), data)
            rows = cursor.fetchall()
            for row in rows:
                if row:
                    yield Email(email_addr=row['email'],
                                message_id=row['message_id'],
                                thread_id=row['thread_id'],
                                sent_at=row['date'],
                                subject=row['subject'],
                                headers=row['header'],
                                body=row['body']
                            )
