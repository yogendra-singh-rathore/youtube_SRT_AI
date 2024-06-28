import moviepy.editor as mp
import pysrt

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
        # Adjust fontsize and position for longer subtitles
        fontsize = 20 if len(sub['text']) > 30 else 24  # Example condition for fontsize adjustment
        txt_clip = mp.TextClip(sub['text'], fontsize=fontsize, color='white', bg_color='black')
        txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(sub['end'] - sub['start'])
        txt_clip = txt_clip.set_start(sub['start'])
        txt_clip = txt_clip.set_fps(24)  # Set text clip fps (e.g., 24 fps)
        txt_clips.append(txt_clip)

    # Composite the video with the subtitles
    final_video = mp.CompositeVideoClip([video, *txt_clips])

    # Write the output video file
    final_video.write_videofile(output_file, codec='libx264', audio_codec='aac', threads=4, fps=24)  # Set overall fps

if __name__ == "__main__":
    mp3_file = "mp3.mp3"
    srt_file = "translated_en.srt"
    output_file = "outputEn2.mp4"
    create_video_with_subtitles(mp3_file, srt_file, output_file)
