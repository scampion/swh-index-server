import os
import logging as log
import binascii

from flask import Flask, abort, Response

SHA1_SIZE_IN_BYTES = 20
SORTED_INDEX_FILEPATH = "data.bin"

log.basicConfig(level=log.INFO)
app = Flask(__name__)
interval = os.stat(SORTED_INDEX_FILEPATH).st_size

i = 1
interval /= 16
while interval > 16:
    i += 1
    interval /= 16


def is_present(query):
    q = bytearray.fromhex(query)
    b = bytearray.fromhex('0' + query[:i])
    idx = int(binascii.hexlify(b), 16)
    pos = int(idx * interval / SHA1_SIZE_IN_BYTES)
    with open(SORTED_INDEX_FILEPATH, "rb") as f:
        f.seek(pos)
        sig = f.read(SHA1_SIZE_IN_BYTES)
        while sig < q:
            sig = f.read(SHA1_SIZE_IN_BYTES)
            if sig >= q:
                break
        while sig > q:
            f.seek(f.tell() - SHA1_SIZE_IN_BYTES * 2)
            sig = f.read(SHA1_SIZE_IN_BYTES)
            if sig <= q:
                break
        return sig == q


def b2a(s):
    return binascii.hexlify(s).decode("ascii")[:10] + "."


@app.route('/')
@app.route('/<string:query>')
def home(query=None):
    if query:
        log.info("query : %s", query)
        if is_present(query):
            return '', 200
        else:
            abort(404)
    else:
        return Response(open('README.md', 'rb').read(), mimetype='text/plain')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)
