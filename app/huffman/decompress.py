import sys
from . import util


def run_decompressor(filename):
    with open(filename, 'rb') as compressed:
        with open(filename+'.decomp', 'wb') as uncompressed:
            util.decompress(compressed, uncompressed)
