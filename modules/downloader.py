import yt_dlp

def baixar_musica(link, download_path, progress_callback=None):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f"{download_path.replace('\\', '/')}/%(title)s.%(ext)s",
        'writethumbnail': True,
        'progress_hooks': [progress_callback] if progress_callback else [],
        'postprocessors': [
            {'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg'},
            {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mka'},
            {'key': 'FFmpegMetadata', 'add_metadata': True},
            {'key': 'EmbedThumbnail'},
        ],
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])