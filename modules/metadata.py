import os
import subprocess
import mutagen
from PIL import Image
from io import BytesIO

def format_time(milliseconds):
    seconds = int(milliseconds / 1000)
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"

def get_file_image(filename, download_path, size=(30, 30)):
    filepath = os.path.join(download_path, filename)
    if not os.path.exists(filepath):
        return None

    img_data = None

    try:
        file = mutagen.File(filepath)
        if file and hasattr(file, 'tags') and file.tags:
            for tag in file.tags.values():
                if hasattr(tag, 'data') and (tag.__class__.__name__ == 'APIC' or 'Picture' in tag.__class__.__name__):
                    img_data = tag.data
                    break
    except Exception:
        pass

    if img_data is None:
        try:
            cmd = [
                'ffmpeg',
                '-i', filepath,
                '-map', '0:v',
                '-f', 'image2pipe',
                '-c:v', 'copy',
                '-vframes', '1',
                '-'
            ]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            output, _ = process.communicate()
            if output:
                img_data = output
        except Exception:
            pass

    if not img_data:
        return None

    try:
        pil_img = Image.open(BytesIO(img_data)).convert('RGBA')
        if size:
            pil_img = pil_img.resize(size, Image.LANCZOS)
        return pil_img
    except Exception:
        return None