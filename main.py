from flask import Flask, request, render_template, redirect
from math import floor
from sqlite3 import OperationalError
import string
import sqlite3

try:
    from urllib.parse import urlparse
    str_encode = str.encode
except ImportError:
    from urlparse import urlparse
    str_encode = str
try:
    from string import ascii_uppercase
    from string import ascii_lowercase
except ImportError:
    from string import lowercase as ascii_lowercase
    from string import uppercase as ascii_uppercase
import base64


def table_check():
    create_table = """
        CREATE TABLE WEB_URL(
        ID INT PRIMARY KEY AUTOINCREMENT,
        URL TEXT NOT NULL    
        );
    """
    # urls.bd better be in app root folder lol
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
        except OperationalError:
            pass


def toBase64(num, b=64):
    if b <= 0 or b > 64:
        return 0
    base = string.digits + string.lowercase + string.uppercase
    r = num % b
    res = base[r]
    q = floor(num/b)
    while q:
        r = q % b
        q = floor(q/b)
        res = base[int(r)] + res
    return res


def toBase10(num, b=64):
    base = string.digits + string.lowercase + string.uppercase
    limit = len(num)
    res = 0
    for i in xrange(limit):
        res = b * res + base.find(num[i])
    return res


@app.route('/', methods = ['GET',   'POST'])
def home():
    if request.method == 'POST':
        original_url = str_encode(request.form.get('url'))
        if urlparse(original_url).scheme == '':
            url = 'http://' + original_url
        else:
            url = original_url
        with sqlite3.connect('urls.db') as conn:
            cursor = conn.cursor()
            res = cursor.execute(
                'INSERT INTO WEB_URL (URL) VALUES(?)',
                [base64.urlsafe_b64decode(url)]
            )
            encoded_string = toBase64(res.lastrowid)
        return render_template('home.html', short_url = host+encoded_string)
    return render_template('home.html')


@app.route('/<short_url>')
def redirect_short_url(short_url):
    decoded = toBase10(short_url)
    url = host
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        res = cursor.execute('SELECT URL FROM WEB_URL WHERE ID=?', [decoded])
        try:
            short = res.fetchone()
            if short is not None:
                url = base64.urlsafe_b64decode(short[0])
        except Exception as e:
            print(e)
    return redirect(url)


if __name__ == '__main__':
    # checks if db was created or not
    table_check()
    app.run(debug=True)
