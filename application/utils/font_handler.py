import os
import platform
import shutil
import subprocess
import requests
from flask import flash
from werkzeug.utils import secure_filename

def install_font(font_path):
    system = platform.system()
    try:
        if system == 'Windows':
            # Copy font to Windows Fonts directory
            font_dest = os.path.join(os.environ['WINDIR'], 'Fonts', os.path.basename(font_path))
            shutil.copy(font_path, font_dest)
            # Add font to registry
            subprocess.run(['reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts', '/v', os.path.basename(font_path), '/t', 'REG_SZ', '/d', font_dest, '/f'], check=True)
        elif system == 'Linux':
            # Copy font to system fonts directory
            font_dest = os.path.join('/usr/share/fonts', os.path.basename(font_path))
            shutil.copy(font_path, font_dest)
            # Refresh font cache
            subprocess.run(['fc-cache', '-f', '-v'], check=True)
        elif system == 'Darwin':  # macOS
            # Copy font to user fonts directory
            font_dest = os.path.join(os.path.expanduser('~/Library/Fonts'), os.path.basename(font_path))
            shutil.copy(font_path, font_dest)
        flash('Font installed successfully!')
    except Exception as e:
        flash(f'Error installing font: {str(e)}')

def download_font_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            font_filename = secure_filename(url.split('/')[-1])
            font_path = os.path.join(os.getcwd(), 'output/fonts', font_filename)
            with open(font_path, 'wb') as f:
                f.write(response.content)
            install_font(font_path)
        else:
            flash('Failed to download font. Please check the URL and try again.')
    except Exception as e:
        flash(f'Error downloading font: {str(e)}')