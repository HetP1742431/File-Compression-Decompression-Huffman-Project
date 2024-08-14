from . import bitio
from . import huffman
import pickle


def read_tree(tree_stream):
    """Read a description of a Huffman tree from the given compressed
    tree stream, and use the pickle module to construct the tree object.
    Then, return the root node of the tree itself.
    Args:
      tree_stream: The compressed stream to read the tree from.
    Returns:
      A Huffman tree root constructed according to the given description.
    """
    huffman_tree = pickle.load(tree_stream)
    return huffman_tree


def decode_byte(tree, bitreader):
    """
    Reads bits from the bit reader and traverses the tree from
    the root to a leaf. Once a leaf is reached, bits are no longer read
    and the value of that leaf is returned.
    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.
      tree: A Huffman tree.
    Returns:
      Next byte of the compressed bit stream.
    """
    while isinstance(tree, huffman.TreeBranch):
        bit = bitreader.readbit()

        if bit == 0:
            tree = tree.getLeft()
        elif bit == 1:
            tree = tree.getRight()
    return tree.getValue()


def decompress(compressed, uncompressed):
    """First, read a Huffman tree from the 'compressed' stream using your
    read_tree function. Then use that tree to decode the rest of the
    stream and write the resulting symbols to the 'uncompressed'
    stream.
    Args:
      compressed: A file stream from which compressed input is read.
      uncompressed: A writable file stream to which the uncompressed
          output is written.
    """
    tree_root = read_tree(compressed)
    bit_read = bitio.BitReader(compressed)
    bit_write = bitio.BitWriter(uncompressed)
    while True:
        decoded_bytes = decode_byte(tree_root, bit_read)
        if decoded_bytes is None:
            break
        else:
            bit_write.writebits(decoded_bytes, 8)
    bit_write.flush()
    return


def write_tree(tree, tree_stream):
    """Write the specified Huffman tree to the given tree_stream
    using pickle.
    Args:
      tree: A Huffman tree.
      tree_stream: The binary file to write the tree to.
    """
    pickle.dump(tree, tree_stream)
    return


def compress(tree, uncompressed, compressed):
    """First write the given tree to the stream 'compressed' using the
    write_tree function. Then use the same tree to encode the data
    from the input stream 'uncompressed' and write it to 'compressed'.
    If there are any partially-written bytes remaining at the end,
    write 0 bits to form a complete byte.
    Flush the bitwriter after writing the entire compressed file.
    Args:
      tree: A Huffman tree.
      uncompressed: A file stream from which you can read the input.
      compressed: A file stream that will receive the tree description
          and the coded input data.
    """
    write_tree(tree, compressed)
    bit_read = bitio.BitReader(uncompressed)
    bit_write = bitio.BitWriter(compressed)
    table = huffman.make_encoding_table(tree)

    while True:
        try:
            byte = bit_read.readbits(8)

            for i in range(len(table[byte])):
                bit_write.writebit(table[byte][i])
        except EOFError:
            for k in range(len(table[None])):
                bit_write.writebit(table[None][k])
            break
    bit_write.flush()
