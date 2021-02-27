import socket
from urllib.parse import urlparse
import pathlib
import sys
import mimetypes

FILEDIR = pathlib.Path('.', '2files')

def parse_http(data):
    text = data.decode('utf-8', 'ignore').splitlines()

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
        'query': parsed_path.query,
        'version': version,
        'headers': headers,
        'data': data
    }

def build_http_reply(reply):
    text = []
    text.append(f'HTTP/1.1 {reply["code"]} {reply["code_desc"]}'.encode())
    for k, v in reply.get('headers', []):
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

def file_reply(path):
    if path.exists():
        if path.is_dir():
            path = FILEDIR / 'kek.html'
        mime = mimetypes.guess_type(path)[0]
        reply = {
            'type': 'reply',
            'code': '200',
            'code_desc': 'OK',
            'headers': [
                ('Content-Type', mime)
            ],
            'data': path.open('rb').read()
        }
        return reply
    else:
        return error_reply(404, desc='Not found')

def reply(parsed):
    if parsed['method'] == 'GET':
        filepath = FILEDIR / pathlib.Path(parsed['path'])
        
        return file_reply(filepath)

    return error_reply(501, 'Not Implemented')

if __name__ == '__main__':
    sock = socket.socket()

    sock.bind(('127.0.0.1', 9092))

    sock.listen(1)
    while True:
        conn, addr = sock.accept()
        print(f'Got connection from {addr}')

        data = conn.recv(1024)

        parsed = parse_http(data)
        rep = build_http_reply(reply(parsed))
        conn.sendall(rep)

        conn.shutdown(socket.SHUT_RDWR)
        conn.close()

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()