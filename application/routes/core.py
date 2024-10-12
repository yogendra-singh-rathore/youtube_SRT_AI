import os
from flask import render_template, send_from_directory, Blueprint

core = Blueprint('core', __name__)

@core.route('/')
def index():
    return render_template('index.html')

@core.route('/output/<folder>/<filename>')
def download_file(folder, filename):
    return send_from_directory(os.path.join(os.getcwd(), f'output/{folder}'), filename)

@core.route('/font', methods=['GET'])
def font():
    return render_template('font.html')

@core.route('/download')
def download():
    output_folders = ['srt_gen', 'srt_edit', 'srt_translated', 'srt_to_mp4']
    files = []

    for folder in output_folders:
        folder_path = os.path.join(os.getcwd(), 'output', folder)
        if os.path.exists(folder_path):
            folder_files = os.listdir(folder_path)
            files.extend([{'name': f, 'path': f'output/{folder}/{f}'} for f in folder_files])

    return render_template('download.html', files=files)

@core.route('/download_output_file/<path:filepath>')
def download_output_file(filepath):
    return send_from_directory(os.path.join(os.getcwd()), filepath, as_attachment=True)