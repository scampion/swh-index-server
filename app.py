import os
from math import floor, ceil
import logging as log
import binascii

from flask import Flask, abort, Response

SHA1_SIZE_IN_BYTES = 20
SORTED_INDEX_FILEPATH = "data.bin"

log.basicConfig(level=log.INFO)
app = Flask(__name__)
mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
index_memory_size = max(1024, mem_bytes - 0.5 * (1024. ** 3) * 80.0 / 100)
index_memory_size = int(os.environ.get('INDEX_MEMORY_SIZE', index_memory_size))
sample_index_interval = int(os.stat(SORTED_INDEX_FILEPATH).st_size / index_memory_size)

log.info("%s bytes of memory available", mem_bytes)
log.info("%s index_memory_size", index_memory_size)
log.info("sorted index size %s", os.stat(SORTED_INDEX_FILEPATH).st_size)
log.info("sample index interval : %d", sample_index_interval)
assert index_memory_size < os.stat(SORTED_INDEX_FILEPATH).st_size, "Binary file fit in memory, exit"


idx = b''
with open(SORTED_INDEX_FILEPATH, "rb") as f:
    sig = f.read(SHA1_SIZE_IN_BYTES)
    i = 0
    while sig:
        f.seek(f.tell() + sample_index_interval)
        sig = f.read(SHA1_SIZE_IN_BYTES)
        idx += sig
        progress = f.tell() / os.stat(SORTED_INDEX_FILEPATH).st_size * 100.0
        print("Indexation in progress : %2d%%" % progress, end='\r')

def b2a(s):
    return binascii.hexlify(s).decode("ascii")[:10] + "."

def get_file_position(q):
    length = len(idx) / SHA1_SIZE_IN_BYTES
    size = floor(length)
    offset = ceil(size / 2) * SHA1_SIZE_IN_BYTES
    sig = idx[offset:offset + SHA1_SIZE_IN_BYTES]
    while q != sig and size > 1:
        log.debug("get file position for query %s : current sig %s position %10s : size %s", b2a(q), b2a(sig), offset, size)
        size = ceil(size / 2.)
        if q > sig:
            offset += size * SHA1_SIZE_IN_BYTES
        if q < sig:
            offset -= size * SHA1_SIZE_IN_BYTES
        sig = idx[offset:offset + SHA1_SIZE_IN_BYTES]
    log.debug("result for file position for query %s : current position %10s : size %s : %s", b2a(q), offset, size, q != sig)
    return offset * sample_index_interval

def is_present(q):
    offset = get_file_position(q)
    with open(SORTED_INDEX_FILEPATH, "rb") as f:
        size = sample_index_interval * 2
        f.seek(offset)
        sig = f.read(SHA1_SIZE_IN_BYTES)
        log.debug("query : %s", b2a(q))
        while q != sig and size > 1:
            log.debug("search %s : current sig %s : position %10s : size %s", b2a(q), b2a(sig), offset, size)
            size = ceil(size / 2.)
            if q > sig:
                offset += size * SHA1_SIZE_IN_BYTES
            if q < sig:
                offset -= size * SHA1_SIZE_IN_BYTES
            f.seek(offset)
            sig = f.read(SHA1_SIZE_IN_BYTES)
        log.debug("search %s : current sig %s : position %10s : size %s", b2a(q), b2a(sig), offset, size)

        return q == sig

@app.route('/')
@app.route('/<string:query>')
def home(query=None):
    if query:
        q = bytearray.fromhex(query)
        log.info("query : %s", b2a(q))
        if is_present(q):
            return '', 200
        else:
            abort(404)
    else:
        return Response(open('README.md', 'rb').read(), mimetype='text/plain')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)
