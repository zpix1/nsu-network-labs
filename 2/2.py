#!/usr/bin/env python3.9

import socket
from urllib.parse import urlparse, parse_qs
import pathlib
import sys
import mimetypes
from datetime import datetime
from collections import defaultdict
import traceback

FILEDIR = pathlib.Path('.', '2files')
DEFAULT_FILE = 'index.html'
SERVER = 'Python Server'
ALWAYS_CLOSE = True
PORT = 9091
TEMPL_EXT = '.pytemp'
NEWLINE = '\r\n'

def my_format(text, query):
    for k, v in query.items():
        text = text.replace("{{" + k + "}}", v[0])
    return text

def httpdate(dt):
    # it is not GMT but NSK time actually but who cares
    """Return a string representation of a date according to RFC 1123
    (HTTP/1.1).

    The supplied date must be in UTC.

    """
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
        dt.year, dt.hour, dt.minute, dt.second)

def parse_http(data):
    text = data.decode('utf-8', 'ignore').splitlines()

    print(f'Parsing: {text[0]}')

    method, full_path, version = text[0].split()

    parsed_path = urlparse(full_path)

    headers = {}

    i = 1

    while i < len(text) and text[i] != '':
        key, value = text[i].split(': ')
        headers[key] = value
        i += 1

    data = NEWLINE.join(text[i + 1:])

    return {
        'type': 'question',
        'method': method,
        'path': parsed_path.path.strip('/'),
        'query': parse_qs(parsed_path.query),
        'version': version,
        'headers': headers,
        'data': data
    }

def build_http_reply(reply_dict):
    text = []

    head = f'HTTP/1.1 {reply_dict["code"]} {reply_dict["code_desc"]}'

    print(f'Sending: {head}')

    text.append(head.encode())
    headers = {
        'Date': httpdate(datetime.now()),
        'Server': SERVER,
        'Content-Length': len(reply_dict.get('data', '')),
        'Content-Type': 'text/plain'
    } | reply_dict.get('headers', {})

    for k, v in headers.items():
        text.append(f'{k}: {v}'.encode())

    text.append(b'')
    text.append(reply_dict.get('data', b''))

    return NEWLINE.encode().join(text)

def error_reply(code, desc='Very bad...'):
    return {
        'type': 'reply',
        'code': str(code),
        'code_desc': desc,
        'data': desc.encode()
    }

def file_reply(textpath, accept, query={}):
    path = FILEDIR / textpath
    if path.exists():
        # path traversal check
        try:
            FILEDIR.joinpath(path).resolve().relative_to(FILEDIR.resolve())
        except ValueError:
            print('PATH TRAVERSAL detected:', path)
            return error_reply(404, desc='Not found')
        
        # pass index file by default
        if path.is_dir():
            path = path / DEFAULT_FILE
            if not path.exists():
                return error_reply(404, desc='Not found')
        
        mime = mimetypes.guess_type(str(path).removesuffix(TEMPL_EXT))[0]

        print(f'Guessed {mime} from {path}')

        if not mime:
            mime = 'text/plain'
        
        if not (mime in accept \
                or '*/*' in accept \
                or mime.split('/')[0] + '/*' in accept):
            return error_reply(415, desc='Unsupported Media Type')

        if str(path).endswith(TEMPL_EXT):
            data = my_format(path.open('r').read(), query).encode()
        else:
            data = path.open('rb').read()

        return {
            'type': 'reply',
            'code': '200',
            'code_desc': 'OK',
            'headers': {
                'Content-Type': mime + '; charset=utf-8',
                'Last-Modified': httpdate(datetime.fromtimestamp(path.stat().st_mtime))
            },
            'data': data
        }
    else:
        return error_reply(404, desc='Not found')

def reply(parsed):
    if parsed['method'] == 'GET':
        return file_reply(parsed['path'], parsed['headers'].get('Accept', ''), parsed['query'])
    elif parsed['method'] == 'HEAD':
        reply_dict = file_reply(parsed['path'], parsed['headers'].get('Accept', ''), parsed['query'])
        del reply_dict['data']
        return reply_dict

    return error_reply(501, 'Not Implemented')

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind(('127.0.0.1', PORT))

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.listen(1)
    while True:
        conn = None
        try:
            conn, addr = sock.accept()

            print(f'Got connection: {addr}')

            requests_done = 0
            while True:
                print('Reading...')
                try:
                    data = conn.recv(10000)
                except socket.timeout:
                    print('Timeout!')
                    break

                print(f'======= Read {len(data):<15} ===============')
                print(data.decode('utf-8', 'ignore'))
                print(f'============================================')

                if len(data) != 0:
                    parsed = parse_http(data)
                    rep = build_http_reply(reply(parsed))
                    requests_done += 1
                    conn.sendall(rep)
                    if parsed['headers'].get('Connection', 'close') == 'close' or ALWAYS_CLOSE:
                        break
                else:
                    break
            print(f'Done {requests_done} requests per connection')
        except Exception as e:
            print('Got error', e)
            traceback.print_exc()
        except KeyboardInterrupt:
            print('Stopped')
            break
        finally:
            if conn:
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()