import yt_dlp


class YouTubeDownloader:
    def __init__(self, url, output_dir="mp3"):
        self.url = url
        self.output_dir = output_dir

    def download(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{self.output_dir}/%(title)s.%(ext)s',
            'writethumbnail': True,
            'postprocessors': [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
                {'key': 'FFmpegMetadata', 'add_metadata': True},
                {'key': 'EmbedThumbnail'},
            ],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=True)

        return info

    @staticmethod
    def es_cancion(info):
        return bool(info.get('track') and info.get('artist'))

    @staticmethod
    def describir(info):
        if YouTubeDownloader.es_cancion(info):
            return f"Canción detectada: {info['artist']} - {info['track']}"
        return f"Contenido genérico: {info.get('title', 'sin título')}"