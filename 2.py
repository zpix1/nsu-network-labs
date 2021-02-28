import socket
from urllib.parse import urlparse, parse_qs
import pathlib
import sys
import mimetypes
from datetime import datetime
from collections import defaultdict

FILEDIR = pathlib.Path('.', '2files')
DEFAULT_FILE = 'index.html'
SERVER = 'Python Server'
ALWAYS_CLOSE = False
PORT = 9091
TEMPL_EXT = '.pytemp'

def my_format(text, query):
    for k, v in query.items():
        text = text.replace("{{" + k + "}}", v[0])
    return text

def httpdate(dt):
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

    while text[i] != '':
        key, value = text[i].split(': ')
        headers[key] = value
        i += 1

    data = '\n'.join(text[i + 1:])

    return {
        'type': 'question',
        'method': method,
        'path': parsed_path.path.strip('/'),
        'query': parse_qs(parsed_path.query),
        'version': version,
        'headers': headers,
        'data': data
    }

def build_http_reply(reply):
    text = []
    head = f'HTTP/1.1 {reply["code"]} {reply["code_desc"]}'
    print(f'Sending: {head}')
    text.append(head.encode())
    headers = reply.get('headers', {})
    headers |= {
        'Date': httpdate(datetime.now()),
        'Server': SERVER,
        'Content-Length': len(reply['data'])
    }
    for k, v in headers.items():
        text.append(f'{k}: {v}'.encode())
    text.append(''.encode())
    text.append(reply.get('data', ''))
    return b'\n'.join(text)

def error_reply(code, desc='Very bad...'):
    return {
        'type': 'reply',
        'code': str(code),
        'code_desc': desc,
        'data': desc.encode()
    }

def file_reply(path, accept, query={}):
    if path.exists():
        try:
            FILEDIR.joinpath(path).resolve().relative_to(FILEDIR.resolve())
        except ValueError:
            return error_reply(404, desc='Not found')
        if path.is_dir():
            path = path / DEFAULT_FILE
            if not path.exists():
                return error_reply(404, desc='Not found')
        mime = mimetypes.guess_type(path)[0]

        if not mime:
            mime = 'text/plain'

        if mime in accept or '*/*' in accept or mime.split('/')[0] + '/*' in accept:
            if str(path).endswith(TEMPL_EXT):
                mime = mimetypes.guess_type(str(path).removesuffix(TEMPL_EXT))[0]
                data = my_format(path.open('r').read(), query).encode()
            else:
                data = path.open('rb').read()

            reply_dict = {
                'type': 'reply',
                'code': '200',
                'code_desc': 'OK',
                'headers': {
                    'Content-Type': mime + '; charset=utf-8',
                    'Last-Modified': httpdate(datetime.fromtimestamp(path.stat().st_mtime))
                },
                'data': data
            }
            return reply_dict
        else:
            return error_reply(415, desc='Unsupported Media Type')
    else:
        return error_reply(404, desc='Not found')

def reply(parsed):
    if parsed['method'] == 'GET':
        filepath = FILEDIR / pathlib.Path(parsed['path'])
        
        return file_reply(filepath, parsed['headers'].get('Accept'), parsed['query'])

    return error_reply(501, 'Not Implemented')

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind(('127.0.0.1', PORT))
    # sock

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.listen(1)
    while True:
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
            print(data.decode())
            print(f'============================================')

            if len(data) != 0:
                parsed = parse_http(data)
                rep = build_http_reply(reply(parsed))
                requests_done += 1
                conn.sendall(rep)
                if parsed['headers'].get('Connection') == 'close' or ALWAYS_CLOSE:
                    break
            else:
                break
        print(f'Done {requests_done} requests per connection')
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()