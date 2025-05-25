from pytubefix import YouTube
import os

class DownloadService:
    def download(self, url: str, output_path: str) -> tuple:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        file = stream.download(output_path=output_path)
        filename = os.path.basename(file)
        return file, filename
