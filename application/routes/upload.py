import os
from application import app
from werkzeug.utils import secure_filename
from application.utils.font_handler import install_font
from flask import request, redirect, url_for, flash, send_from_directory, Blueprint

upload = Blueprint('upload', __name__)

@upload.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'output/srt_to_mp4'), filename)

@upload.route('/upload_font', methods=['POST'])
def upload_font():
    try:
        font_file = request.files.get('font_file')
        
        if not font_file:
            flash('No font file uploaded.')
            return redirect(url_for('core.font'))
        
        font_filename = secure_filename(font_file.filename)
        output_fonts_dir = os.path.join(os.getcwd(), 'output/fonts')
        if not os.path.exists(output_fonts_dir):
            os.makedirs(output_fonts_dir)
        
        font_path = os.path.join(output_fonts_dir, font_filename)
        font_file.save(font_path)
        install_font(font_path)
        
        flash(f'Font {font_filename} uploaded and installed successfully.')
    except Exception as e:
        flash(f'Error uploading font: {str(e)}')
    
    return redirect(url_for('core.font'))