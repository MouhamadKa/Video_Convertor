import os
import ffmpeg
from django.conf import settings
from .models import Videos

def convert_video_to_mpd(video_id):
    video = Videos.objects.get(id=video_id)
    input_path = video.video_file.path
    output_path = os.path.splitext(input_path)[0] + '.mpd'
    
    # Convert the video to .mpd format using FFmpeg
    try:
        print(f"Converting video: {input_path} to {output_path}")
        ffmpeg.input(input_path).output(output_path, f='dash').run(capture_stdout=True, capture_stderr=True)
        print(f"Video converted successfully: {output_path}")
        
        # Update the video model with the new file path
        video.video_file.name = os.path.relpath(output_path, settings.MEDIA_ROOT)
        video.save()
        return True
    except ffmpeg._run.Error as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
