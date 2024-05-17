from celery import shared_task
from .models import Videos
import subprocess
import os

@shared_task
def convert_video(video_id):
    try:
        video = Videos.objects.get(id=video_id)
        input_path = video.file.path
        output_path = os.path.splitext(input_path)[0] + '.mpd'
        
        # Conversion command using ffmpeg
        command = [
            'ffmpeg',
            '-i', input_path,
            '-map', '0',
            '-preset', 'fast',
            '-profile:v', 'main',
            '-keyint_min', '48',
            '-g', '48',
            '-sc_threshold', '0',
            '-b:v', '500k',
            '-maxrate', '500k',
            '-bufsize', '1000k',
            '-b:a', '128k',
            '-f', 'dash',
            '-y', output_path
        ]
        
        subprocess.run(command, check=True)
        
        # Update video model with new file path if needed
        video.file.name = os.path.basename(output_path)
        video.save()
        print("Successfully converted!")
    except Videos.DoesNotExist:
        print(f"Video with ID {video_id} does not exist.")
    except subprocess.CalledProcessError:
        print("Conversion failed!")
    except Exception as e:
        print(f"An error occurred: {e}")