from bs4 import BeautifulSoup
import csv
from pprint import pprint

import re
import sys

in_file = sys.argv[1]
out_file = sys.argv[2]

err_output = open('error.txt', 'w')

def remove_header(row):
    ''' folishly detect the header of messaegs'''
    patterns = [
        r'[hH][Ii]\s\w+(?:!|,)',
        r'[hH]ello\s\w+(?:!|,)?',
        r'(?:[dD]ear|[hH][iI])\s\w+(?:!|,)?',
        r'(?:[dD]ears)(?:!|,)?\n',
    ]
    match = None
    for pattern in patterns:
        match = re.search(pattern, row)
        if match:
            row = row[match.end():]
            break
    if not match:
        print>>err_output, '[-----------------no header-----------------]\n', row, '\n\n'
    return row.strip()

def remove_footer(row):
    ''' folishly remove the footer of messages '''
    patterns = [
        r'[bB]est\s[rR]egards(?:!|,|\n)',
        r'[kK]ind\s[rR]egards(?:!|,|\n)',
        r'[tT]hank\s[yY]ou(?:!|,|\n)',
        r'[rR]egards(?:!|,|\n)',
        r'[bB]est(?:!|,|\n)',
        r'(?:^|\n)--\s\n',
    ]
    match = None
    for pattern in patterns:
        match = re.search(pattern, row)
        if match:
            row = row[:match.start()]
            break
    if not match:
        print>>err_output, '[-----------------no footer-----------------]\n', row, '\n\n'
    return row.strip()


def sanitize(raw):
    # basic.
    text = raw
    text = text.replace('\r', '')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&nbsp;', ' ')
    soup = BeautifulSoup(text)
    text = soup.get_text()
    text = ''.join([i if ord(i) < 128 else ' ' for i in text])
    #text = text.decode('unicode_escape').encode('ascii', 'ignore')

    # remove header and footer.
    text = remove_header(text)
    text = remove_footer(text)
    return text


with open(in_file, 'rU') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    print rows[0].keys()

with open(out_file, 'w') as f:
    header = ['original_email', 'response_email', 'user_email_id', 'email_id', 'thread_id']
    writer = csv.DictWriter(f, header)
    writer.writeheader()
    for row in rows:
        data = {key: row[key] for key in header}
        data['original_email'] = sanitize(data['original_email'])
        data['response_email'] = sanitize(data['response_email'])
        writer.writerow(data)


