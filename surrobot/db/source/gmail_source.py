# extract emails from Gmail source
import gmail
from oauth2client import client as auth_client
from sys import stderr

from surrobot.config import GOOGLE_CLIENT_SECRET, GOOGLE_DB_FILE_NAME
from surrobot.db.db import sql, DBConn


class AccessTokenDBConn(DBConn):
    def __enter__(self):
        conn = sql.connect(GOOGLE_DB_FILE_NAME)
        conn.row_factory = sql.Row
        # manages access tokens for user's email account.
        conn.execute("""CREATE TABLE IF NOT EXISTS access
                    (email text,
                    access_token text
                    )""")

        conn.commit()
        self.conn = conn
        return conn

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()


class AccessTokenDB(object):
    '''
    manages the interface with db to save and retrieve access_tokens.
    '''

    @staticmethod
    def get(email_addr):
        with AccessTokenDBConn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                    SELECT * FROM access WHERE email=:email
                    ''', dict(email=email_addr))
            row = cursor.fetchone()
            if row:
                return row['access_token']
        return ''


    @staticmethod
    def save(email_addr, access_token):
        with AccessTokenDBConn() as conn:
            cursor = conn.cursor()
            if not AccessTokenDB.get(email_addr):
                cursor.execute('''
                        INSERT INTO access
                        (email, access_token)
                        VALUES
                        (:email, :access_token)
                        ''',
                        dict(email=email_addr, access_token=access_token))
            else:
                cursor.execute('''
                        UPDATE access
                        SET access_token=:access_token
                        WHERE email=:email
                        ''',
                        dict(email=email_addr, access_token=access_token))


class AccessToken(object):
    '''
    the interface to obtain an access token
    '''
    @staticmethod
    def get(email_addr):
        token = AccessTokenDB.get(email_addr)
        if not token:
            return AccessToken.refresh(email_addr)
        return token


    @staticmethod
    def refresh(email_addr):
        token = access_token(GOOGLE_CLIENT_SECRET)
        print 'access_token', token
        AccessTokenDB.save(email_addr, token)
        return token


def extract(email_addr, access_token, domain='inbox'):
    client = gmail.authenticate(email_addr, access_token)
    return getattr(client, domain)().mail()


def access_token(secrets_json_path='client_secrets.json'):
    flow = auth_client.flow_from_clientsecrets(
        'client_secrets.json',
        scope='https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email https://mail.google.com/',
        redirect_uri='http://127.0.0.1/oauth2callback',
    )
    auth_uri = flow.step1_get_authorize_url()
    print 'please follow link: ', auth_uri
    auth_code = raw_input('authorization code: ')
    print 'auth_code', auth_code
    credentials = flow.step2_exchange(auth_code)
    access_token_info = credentials.get_access_token()
    print access_token_info
    token = access_token_info.access_token
    return token


def sync(email_addr):
    try:
        messages = extract(
                email_addr=email_addr,
                access_token=AccessToken.get(email_addr),
                domain='all_mail')

        def fetch_messages():
            for (mi, message) in enumerate(messages):
                if mi <= 24998:
                    print '[%d] skip' % mi
                    continue
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
