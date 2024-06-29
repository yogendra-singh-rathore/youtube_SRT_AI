import os
import platform
import shutil
import subprocess
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import moviepy.editor as mp
import pysrt
from werkzeug.utils import secure_filename
from deep_translator import GoogleTranslator
import assemblyai as aai

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key

# Set the ImageMagick path
if os.name == 'nt':  # Windows
    os.environ['IMAGEMAGICK_BINARY'] = r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"  # Update with your ImageMagick path
else:
    os.environ['IMAGEMAGICK_BINARY'] = "/usr/bin/convert"  # Update if necessary for Linux/Mac

# Create output directories
os.makedirs(os.path.join(os.getcwd(), 'output/srt_gen'), exist_ok=True)
os.makedirs(os.path.join(os.getcwd(), 'output/srt_edit'), exist_ok=True)
os.makedirs(os.path.join(os.getcwd(), 'output/srt_to_mp4'), exist_ok=True)
os.makedirs(os.path.join(os.getcwd(), 'uploads'), exist_ok=True)
os.makedirs(os.path.join(os.getcwd(), 'output/fonts'), exist_ok=True)

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

def srt_to_text(srt_file):
    subs = pysrt.open(srt_file)
    text_lines = []
    for sub in subs:
        start = sub.start.ordinal / 1000  # Convert to seconds
        end = sub.end.ordinal / 1000  # Convert to seconds
        text_lines.append({'start': start, 'end': end, 'text': sub.text})
    return text_lines

def create_video_with_subtitles(mp3_file, srt_file, output_file, font_path=None):
    # Load the MP3 audio file
    audio = mp.AudioFileClip(mp3_file)
    audio = audio.set_fps(44100)  # Set audio fps (typically 44100 Hz)

    # Create a blank video clip with the same duration as the audio
    video = mp.ColorClip(size=(1280, 720), color=(0, 0, 0), duration=audio.duration)
    video = video.set_audio(audio)
    video = video.set_fps(24)  # Set video fps (e.g., 24 fps)

    # Load subtitles
    subtitles = srt_to_text(srt_file)

    # Add subtitles to the video
    txt_clips = []
    for sub in subtitles:
        fontsize = 50
        txt_clip = mp.TextClip(sub['text'], fontsize=fontsize, font=font_path if font_path else 'Arial', color='white', bg_color='black', method='caption', size=(video.size[0] - 100, None))
        txt_clip = txt_clip.set_position(('center', 'center')).set_duration(sub['end'] - sub['start'])
        txt_clip = txt_clip.set_start(sub['start'])
        txt_clip = txt_clip.set_fps(24)
        txt_clips.append(txt_clip)

    # Composite the video with the subtitles
    final_video = mp.CompositeVideoClip([video, *txt_clips])

    # Write the output video file
    final_video.write_videofile(output_file, codec='libx264', audio_codec='aac', threads=4, fps=24)




def translate_text(text, source_language, target_language):
    translator = GoogleTranslator(source=source_language, target=target_language)
    return translator.translate(text)

def translate_srt(file_path, intermediate_language, target_languages):
    # Read the original SRT file
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Translate the text to the intermediate language (English)
    translated_lines_to_intermediate = []
    for line in lines:
        if not line.strip() or line[0].isdigit() or '-->' in line:
            translated_lines_to_intermediate.append(line)
        else:
            translated_text = translate_text(line, 'auto', intermediate_language)
            translated_lines_to_intermediate.append(translated_text + '\n')

    # Save the intermediate language file
    intermediate_file_path = f'output/srt_gen/trans_intermediate_{intermediate_language}.srt'
    os.makedirs('output/srt_gen', exist_ok=True)
    with open(intermediate_file_path, 'w', encoding='utf-8') as file:
        file.writelines(translated_lines_to_intermediate)

    print(f"Subtitles translated to {intermediate_language} saved to {intermediate_file_path}")

    # Translate the intermediate language file to other target languages
    for target_language in target_languages:
        translated_lines_to_target = []
        for line in translated_lines_to_intermediate:
            if not line.strip() or line[0].isdigit() or '-->' in line:
                translated_lines_to_target.append(line)
            else:
                translated_text = translate_text(line, intermediate_language, target_language)
                translated_lines_to_target.append(translated_text + '\n')

        output_file_path = f'output/srt_gen/trans_{target_language}.srt'
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.writelines(translated_lines_to_target)

        print(f"Subtitles translated to {target_language} saved to {output_file_path}")

# def get_font_url(language_code):
#     font_urls = {
#         'hi': 'https://example.com/fonts/hindi.ttf',  # Replace with actual font URLs
#         'zh': 'https://example.com/fonts/chinese.ttf',
#         'ja': 'https://example.com/fonts/japanese.ttf',
#     }
#     return font_urls.get(language_code)

# def download_font(font_url, font_path):
#     response = requests.get(font_url)
#     with open(font_path, 'wb') as file:
#         file.write(response.content)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/srt_gen', methods=['GET', 'POST'])
def srt_gen():
    if request.method == 'POST':
        language_code = request.form['language']
        file = request.files['file']
        api_key = request.form['api_key']  # Get the API key from the form

        if file:
            file_path = os.path.join(os.getcwd(), 'output/srt_gen', secure_filename(file.filename))
            file.save(file_path)

            # Set AssemblyAI API key
            aai.settings.api_key = api_key

            transcriber = aai.Transcriber(config=aai.TranscriptionConfig(language_code=language_code))
            transcript = transcriber.transcribe(file_path)

            if transcript.status == aai.TranscriptStatus.error:
                flash('Transcription error: ' + transcript.error)
            else:
                srt_data = transcript.export_subtitles_srt()
                vtt_data = transcript.export_subtitles_vtt()
                base_filename = os.path.splitext(file.filename)[0]

                srt_output_path = os.path.join(os.getcwd(), f'output/srt_gen/{base_filename}_{language_code}.srt')
                vtt_output_path = os.path.join(os.getcwd(), f'output/srt_gen/{base_filename}_{language_code}.vtt')

                with open(srt_output_path, "w", encoding="utf-8") as f:
                    f.write(srt_data)

                with open(vtt_output_path, "w", encoding="utf-8") as f:
                    f.write(vtt_data)

                flash('Subtitles generated successfully!')
                return redirect(url_for('srt_gen'))

    return render_template('srt_gen.html')

@app.route('/srt_edit', methods=['GET', 'POST'])
def srt_edit():
    srt_files = os.listdir(os.path.join(os.getcwd(), 'output/srt_gen'))
    video_files = os.listdir(os.path.join(os.getcwd(), 'output/srt_to_mp4'))

    if request.method == 'POST':
        response_data = {}

        if 'file_content' in request.form:
            file_content = request.form['file_content']
            file_path = request.form['file_path']
            custom_name = request.form['custom_name']
            if custom_name:
                base_filename, ext = os.path.splitext(file_path)
                new_file_path = os.path.join(os.getcwd(), 'output/srt_edit', secure_filename(custom_name + ext))
            else:
                new_file_path = os.path.join(os.getcwd(), 'output/srt_edit', secure_filename(os.path.basename(file_path)))
            with open(new_file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            flash('File saved successfully!')
            return redirect(url_for('srt_edit'))

        if 'file' in request.form:
            srt_file_name = request.form['file']
            srt_file_path = os.path.join(os.getcwd(), 'output/srt_gen', srt_file_name)
            with open(srt_file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            response_data['file_content'] = file_content
            response_data['file_path'] = srt_file_path

        if 'video' in request.form:
            video_file_name = request.form['video']
            video_file_path = os.path.join(os.getcwd(), 'output/srt_to_mp4', video_file_name)
            response_data['video_path'] = url_for('uploaded_file', filename=secure_filename(video_file_name))

        response_data['srt_files'] = srt_files
        response_data['video_files'] = video_files

        return jsonify(response_data)

    return render_template('srt_edit.html', srt_files=srt_files, video_files=video_files)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'output/srt_to_mp4'), filename)

@app.route('/srt_translate', methods=['GET', 'POST'])
def srt_translate():
    srt_files = os.listdir(os.path.join(os.getcwd(), 'output/srt_gen'))
    
    if request.method == 'POST':
        file_name = request.form['file']
        intermediate_language = request.form['intermediate_language']
        target_languages = request.form.getlist('target_languages')

        if file_name:
            file_path = os.path.join('output/srt_gen', secure_filename(file_name))

            translate_srt(file_path, intermediate_language, target_languages)

            flash('Subtitles translated successfully!')
            return redirect(url_for('srt_translate'))

    return render_template('srt_translate.html', srt_files=srt_files)

@app.route('/srt_to_mp4', methods=['GET', 'POST'])
def srt_to_mp4():
    mp3_files = os.listdir(os.path.join(os.getcwd(), 'output/srt_gen'))
    srt_files = os.listdir(os.path.join(os.getcwd(), 'output/srt_gen'))
    if request.method == 'POST':
        mp3_file_name = request.form['mp3_file']
        srt_file_name = request.form['srt_file']
        output_file_name = request.form['output_file_name']
        font_path = request.form.get('font_path')  # Get the font path if provided

        mp3_path = os.path.join(os.getcwd(), 'output/srt_gen', secure_filename(mp3_file_name))
        srt_path = os.path.join(os.getcwd(), 'output/srt_gen', secure_filename(srt_file_name))

        if mp3_file_name and srt_file_name:
            output_file_path = os.path.join(os.getcwd(), 'output/srt_to_mp4', secure_filename(output_file_name))
            create_video_with_subtitles(mp3_path, srt_path, output_file_path, font_path)
            flash('Video with subtitles created successfully!')
            return redirect(url_for('srt_to_mp4'))

    return render_template('srt_to_mp4.html', mp3_files=mp3_files, srt_files=srt_files, fonts=os.listdir('output/fonts'))




@app.route('/output/<folder>/<filename>')
def download_file(folder, filename):
    return send_from_directory(os.path.join(os.getcwd(), f'output/{folder}'), filename)

@app.route('/font', methods=['GET'])
def font():
    return render_template('font.html')

@app.route('/upload_font', methods=['POST'])
def upload_font():
    try:
        font_file = request.files.get('font_file')
        
        if not font_file:
            flash('No font file uploaded.')
            return redirect(url_for('font'))
        
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
    
    return redirect(url_for('font'))

@app.route('/download')
def download():
    output_folders = ['srt_gen', 'srt_edit', 'srt_translated', 'srt_to_mp4']
    files = []

    for folder in output_folders:
        folder_path = os.path.join(os.getcwd(), 'output', folder)
        if os.path.exists(folder_path):
            folder_files = os.listdir(folder_path)
            files.extend([{'name': f, 'path': f'output/{folder}/{f}'} for f in folder_files])

    return render_template('download.html', files=files)

@app.route('/download_output_file/<path:filepath>')
def download_output_file(filepath):
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    return send_from_directory(directory, filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=int("3000"),debug=True)