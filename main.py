from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import os
import assemblyai as aai
from deep_translator import GoogleTranslator
import moviepy.editor as mp
import pysrt
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key

# Enter Your API key Here
aai.settings.api_key = "API KEY"

# Create output directories
os.makedirs('output/srt_gen', exist_ok=True)
os.makedirs('output/srt_edit', exist_ok=True)
os.makedirs('output/srt_translated', exist_ok=True)
os.makedirs('output/srt_to_mp4', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

def srt_to_text(srt_file):
    subs = pysrt.open(srt_file)
    text_lines = []
    for sub in subs:
        start = sub.start.ordinal / 1000  # Convert to seconds
        end = sub.end.ordinal / 1000  # Convert to seconds
        text_lines.append({'start': start, 'end': end, 'text': sub.text})
    return text_lines

def create_video_with_subtitles(mp3_file, srt_file, output_file):
    # Load the MP3 audio file
    audio = mp.AudioFileClip(mp3_file)
    audio = audio.set_fps(44100)  # Set audio fps (typically 44100 Hz)

    # Create a blank video clip with the same duration as the audio
    video = mp.ColorClip(size=(1280, 720), color=(0, 0, 0), duration=audio.duration)  # Increased resolution
    video = video.set_audio(audio)
    video = video.set_fps(24)  # Set video fps (e.g., 24 fps)

    # Load subtitles
    subtitles = srt_to_text(srt_file)

    # Add subtitles to the video
    txt_clips = []
    for sub in subtitles:
        # Set larger fontsize for better readability and ensure it fits within the screen
        fontsize = 50
        txt_clip = mp.TextClip(sub['text'], fontsize=fontsize, color='white', bg_color='black', method='caption', size=(video.size[0] - 100, None))  # Adjust the size to fit within the screen
        txt_clip = txt_clip.set_position(('center', 'center')).set_duration(sub['end'] - sub['start'])  # Center the text
        txt_clip = txt_clip.set_start(sub['start'])
        txt_clip = txt_clip.set_fps(24)  # Set text clip fps (e.g., 24 fps)
        txt_clips.append(txt_clip)

    # Composite the video with the subtitles
    final_video = mp.CompositeVideoClip([video, *txt_clips])

    # Write the output video file
    final_video.write_videofile(output_file, codec='libx264', audio_codec='aac', threads=4, fps=24)  # Set overall fps


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
    intermediate_file_path = f'output/srt_translated/trans_intermediate_{intermediate_language}.srt'
    os.makedirs('output/srt_translated', exist_ok=True)
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

        output_file_path = f'output/srt_translated/trans_{target_language}.srt'
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.writelines(translated_lines_to_target)

        print(f"Subtitles translated to {target_language} saved to {output_file_path}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/srt_gen', methods=['GET', 'POST'])
def srt_gen():
    if request.method == 'POST':
        language_code = request.form['language']
        file = request.files['file']
        if file:
            file_path = os.path.join('output/srt_gen', file.filename)
            file.save(file_path)

            transcriber = aai.Transcriber(config=aai.TranscriptionConfig(language_code=language_code))
            transcript = transcriber.transcribe(file_path)

            if transcript.status == aai.TranscriptStatus.error:
                flash('Transcription error: ' + transcript.error)
            else:
                srt_data = transcript.export_subtitles_srt()
                vtt_data = transcript.export_subtitles_vtt()
                base_filename = os.path.splitext(file.filename)[0]

                srt_output_path = f'output/srt_gen/{base_filename}_{language_code}.srt'
                vtt_output_path = f'output/srt_gen/{base_filename}_{language_code}.vtt'

                with open(srt_output_path, "w", encoding="utf-8") as f:
                    f.write(srt_data)

                with open(vtt_output_path, "w", encoding="utf-8") as f:
                    f.write(vtt_data)

                flash('Subtitles generated successfully!')
                return redirect(url_for('srt_gen'))

    return render_template('srt_gen.html')

@app.route('/srt_edit', methods=['GET', 'POST'])
def srt_edit():
    if request.method == 'POST':
        response_data = {}

        if 'file' in request.files:
            srt_file = request.files['file']
            if srt_file:
                srt_file_path = os.path.join('output/srt_edit', secure_filename(srt_file.filename))
                srt_file.save(srt_file_path)
                with open(srt_file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                response_data['file_content'] = file_content
                response_data['file_path'] = srt_file_path

        if 'video' in request.files:
            video_file = request.files['video']
            if video_file:
                video_file_path = os.path.join('output/srt_edit', secure_filename(video_file.filename))
                video_file.save(video_file_path)
                response_data['video_path'] = url_for('uploaded_file', filename=secure_filename(video_file.filename))

        return response_data

    return render_template('srt_edit.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('output/srt_edit', filename)

@app.route('/srt_translate', methods=['GET', 'POST'])
def srt_translate():
    if request.method == 'POST':
        file = request.files['file']
        intermediate_language = request.form['intermediate_language']
        target_languages = request.form.getlist('target_languages')

        if file:
            file_path = os.path.join('output/srt_translated', secure_filename(file.filename))
            file.save(file_path)

            translate_srt(file_path, intermediate_language, target_languages)

            flash('Subtitles translated successfully!')
            return redirect(url_for('srt_translate'))

    return render_template('srt_translate.html')

@app.route('/srt_to_mp4', methods=['GET', 'POST'])
def srt_to_mp4():
    if request.method == 'POST':
        mp3_file = request.files['mp3_file']
        srt_file = request.files['srt_file']
        output_file_name = request.form['output_file_name']

        if mp3_file and srt_file:
            mp3_path = os.path.join('uploads', secure_filename(mp3_file.filename))
            srt_path = os.path.join('uploads', secure_filename(srt_file.filename))
            mp3_file.save(mp3_path)
            srt_file.save(srt_path)

            output_file_path = os.path.join('output/srt_to_mp4', secure_filename(output_file_name))

            create_video_with_subtitles(mp3_path, srt_path, output_file_path)

            flash('Video with subtitles created successfully!')
            return redirect(url_for('srt_to_mp4'))

    return render_template('srt_to_mp4.html')

@app.route('/output/<folder>/<filename>')
def download_file(folder, filename):
    return send_from_directory(f'output/{folder}', filename)

if __name__ == '__main__':
    app.run(debug=True)