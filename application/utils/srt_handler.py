import pysrt
import moviepy.editor as mp
import os
from deep_translator import GoogleTranslator

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
