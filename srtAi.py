# Start by making sure the `assemblyai` package is installed.
# If not, you can install it by running the following command:
# pip install -U assemblyai
#
# Note: Some macOS users may need to use `pip3` instead of `pip`.

import assemblyai as aai

# Replace with your API key
aai.settings.api_key = "Enter Your API KEY"

# URL of the file to transcribe
FILE_URL = "input.mp3"

# You can also transcribe a local file by passing in a file path
# FILE_URL = './path/to/file.mp3'
# Visit This website to Find languae Code https://www.assemblyai.com/docs/concepts/supported-languages
language = aai.TranscriptionConfig(language_code="hi") # Hindi Language = hi, English = en

transcriber = aai.Transcriber(config=language)
transcript = transcriber.transcribe(FILE_URL)

if transcript.status == aai.TranscriptStatus.error:
    print(transcript.error)
else:
    srt_data = transcript.export_subtitles_srt()
    vtt_data = transcript.export_subtitles_vtt()

    with open("output.srt", "w", encoding="utf-8") as f:
        f.write(srt_data)  # Directly write SRT data as a string

    with open("output.vtt", "w", encoding="utf-8") as f:
        f.write(vtt_data)  # Directly write VTT data as a string

    print("Subtitles generated! Check output.srt and output.vtt files.")