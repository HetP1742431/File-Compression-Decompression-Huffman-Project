from . import huffman
from . import util


def run_compressor(filename):
    with open(filename, 'rb') as uncompressed:
        freqs = huffman.make_freq_table(uncompressed)
        tree = huffman.make_tree(freqs)
        uncompressed.seek(0)
        with open(filename+'.huf', 'wb') as compressed:
            util.compress(tree, uncompressed, compressed)
