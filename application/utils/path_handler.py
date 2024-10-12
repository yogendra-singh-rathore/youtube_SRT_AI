import os

def paths():
    # Create output directories
    os.makedirs(os.path.join(os.getcwd(), 'output/srt_gen'), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), 'output/srt_edit'), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), 'output/srt_to_mp4'), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), 'uploads'), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), 'output/fonts'), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), 'output/database'), exist_ok=True)