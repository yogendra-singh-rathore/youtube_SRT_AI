import os
import assemblyai as aai
from application import app
from werkzeug.utils import secure_filename
from flask import render_template, request, flash, redirect, url_for, jsonify, Blueprint
from application.utils.srt_handler import translate_srt, create_video_with_subtitles

srt = Blueprint('srt', __name__)

@srt.route('/srt_gen', methods=['GET', 'POST'])
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
                return redirect(url_for('srt.srt_gen'))

    return render_template('srt_gen.html')

@srt.route('/srt_edit', methods=['GET', 'POST'])
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
            return redirect(url_for('srt.srt_edit'))

        if 'file' in request.form:
            srt_file_name = request.form['file']
            srt_file_path = os.path.join(os.getcwd(), 'output/srt_gen', srt_file_name)
            with open(srt_file_path, 'r', encoding='utf-8') as f:
                print(srt_file_path)
                file_content = f.read()
            response_data['file_content'] = file_content
            response_data['file_path'] = srt_file_path

        if 'video' in request.form:
            video_file_name = request.form['video']
            video_file_path = os.path.join(os.getcwd(), 'output/srt_to_mp4', video_file_name)
            response_data['video_path'] = url_for('upload.uploaded_file', filename=secure_filename(video_file_name))

        response_data['srt_files'] = srt_files
        response_data['video_files'] = video_files

        return jsonify(response_data)

    return render_template('srt_edit.html', srt_files=srt_files, video_files=video_files)

@srt.route('/srt_translate', methods=['GET', 'POST'])
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
            return redirect(url_for('srt.srt_translate'))

    return render_template('srt_translate.html', srt_files=srt_files)

@srt.route('/srt_to_mp4', methods=['GET', 'POST'])
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
            return redirect(url_for('srt.srt_to_mp4'))

    return render_template('srt_to_mp4.html', mp3_files=mp3_files, srt_files=srt_files, fonts=os.listdir('output/fonts'))
