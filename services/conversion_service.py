from moviepy import VideoFileClip, AudioFileClip
import os

class ConversionService:
    def convert(self, input_path: str, output_path: str, output_format: str):
        _, ext = os.path.splitext(input_path)
        ext = ext.lower()

        if ext in [".mp4", ".avi", ".mov", ".mkv"]:
            clip = VideoFileClip(input_path)

            if output_format in ["mp3", "wav"]:
                clip.audio.write_audiofile(output_path)
            elif output_format == "mp4":
                clip.write_videofile(output_path)
            else:
                raise Exception("Formato não suportado para vídeo.")

            clip.close()

        elif ext in [".mp3", ".wav"]:
            audio_clip = AudioFileClip(input_path)
            audio_clip.write_audiofile(output_path)
            audio_clip.close()

        else:
            raise Exception("Formato de arquivo não suportado para conversão.")
