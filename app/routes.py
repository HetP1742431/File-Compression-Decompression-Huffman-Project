from flask import Blueprint, render_template, request, redirect, url_for, send_file, flash, after_this_request
import os
import shutil
import tempfile
from io import BytesIO
from .huffman import compress, decompress

main = Blueprint('main', __name__)

# Use absolute paths to avoid path issues
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
COMPRESSED_FOLDER = os.path.join(BASE_DIR, 'compressed')
DECOMPRESSED_FOLDER = os.path.join(BASE_DIR, 'decompressed')

# Ensure the folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)
os.makedirs(DECOMPRESSED_FOLDER, exist_ok=True)


@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'compress':
            return handle_compression()
        elif action == 'decompress':
            return handle_decompression()

    return render_template('index.html')


def handle_compression():
    if 'file' not in request.files:
        flash("No file part", "error")
        return redirect(url_for('main.index'))

    file = request.files['file']
    if file.filename == '':
        flash("No selected file", "error")
        return redirect(url_for('main.index'))

    filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Remove existing files to avoid overwrite errors
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(os.path.join(COMPRESSED_FOLDER, filename + '.huf')):
        os.remove(os.path.join(COMPRESSED_FOLDER, filename + '.huf'))

    file.save(file_path)

    compressed_file_path = compress_file(file_path)
    if compressed_file_path:
        # Read the file into memory
        with open(compressed_file_path, 'rb') as f:
            data = BytesIO(f.read())

        # Schedule file removal after it has been downloaded
        @after_this_request
        def remove_file(response):
            try:
                os.remove(compressed_file_path)
            except Exception as e:
                print(f"Error removing file {compressed_file_path}: {e}")
            return response

        # Serve the file from memory
        data.seek(0)
        return send_file(data, as_attachment=True, download_name=os.path.basename(compressed_file_path))
    else:
        flash("Compression failed", "error")
        return redirect(url_for('main.index'))


def handle_decompression():
    if 'file' not in request.files:
        flash("No file part", "error")
        return redirect(url_for('main.index'))

    file = request.files['file']
    if file.filename == '':
        flash("No selected file", "error")
        return redirect(url_for('main.index'))

    filename = file.filename
    file_path = os.path.join(COMPRESSED_FOLDER, filename)

    # Remove existing files to avoid overwrite errors
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(os.path.join(DECOMPRESSED_FOLDER, filename.replace('.huf', ''))):
        os.remove(os.path.join(DECOMPRESSED_FOLDER,
                  filename.replace('.huf', '')))

    file.save(file_path)

    decompressed_file_path = decompress_file(file_path)
    if decompressed_file_path:
        # Read the file into memory
        with open(decompressed_file_path, 'rb') as f:
            data = BytesIO(f.read())

        # Schedule file removal after it has been downloaded
        @after_this_request
        def remove_file(response):
            try:
                os.remove(decompressed_file_path)
            except Exception as e:
                print(f"Error removing file {decompressed_file_path}: {e}")
            return response

        # Serve the file from memory
        data.seek(0)
        return send_file(data, as_attachment=True, download_name=os.path.basename(decompressed_file_path))
    else:
        flash("Decompression failed", "error")
        return redirect(url_for('main.index'))


def compress_file(file_path):
    compressed_file_path = os.path.join(
        COMPRESSED_FOLDER, os.path.basename(file_path) + '.huf')
    try:
        compress.run_compressor(file_path)
        # Move compressed file to the correct folder
        os.rename(file_path + '.huf', compressed_file_path)
        os.remove(file_path)  # Remove the uploaded file after compression
        return compressed_file_path
    except Exception as e:
        print(f"Error during compression: {e}")
        return None


def decompress_file(file_path):
    decompressed_file_path = os.path.join(
        DECOMPRESSED_FOLDER, os.path.basename(file_path).replace('.huf', ''))
    try:
        decompress.run_decompressor(file_path)
        # Move decompressed file to the correct folder
        os.rename(file_path + '.decomp', decompressed_file_path)
        os.remove(file_path)  # Remove the compressed file after decompression
        return decompressed_file_path
    except Exception as e:
        print(f"Error during decompression: {e}")
        return None
