import os
import subprocess
from django.conf import settings
from .models import Videos  # Adjust to your actual model


def convert_video_to_mpd(vid_id):
    try:
        # Fetch the video instance from the database
        video = Videos.objects.get(id=vid_id)

        # Define the base directory where videos are stored
        base_dir = settings.MEDIA_ROOT

        # Create a directory named after the video id
        video_dir = os.path.join(base_dir, os.path.join("post_videos", str(video.id)))
        os.makedirs(video_dir, exist_ok=True)

        # Define the path for the original video and the output .mpd file
        original_video_path = video.video_file.path
        output_mpd_path = os.path.join(video_dir, f"{video._meta.fields.name}.mpd")
        print("XXXXXXXXXXXXXXXXXXXXXXX")
        print(output_mpd_path)

        # Command to convert video to DASH using ffmpeg
        cmd = [
            'ffmpeg',
            '-i', original_video_path,
            '-codec:v', 'libx264',  # Video codec
            '-codec:a', 'aac',      # Audio codec
            '-b:v', '1000k',        # Video bitrate
            '-b:a', '128k',         # Audio bitrate
            '-s', '640x360',        # Output resolution
            '-map', '0',            # Map all streams
            '-f', 'dash',           # Format for MPEG-DASH
            '-init_seg_name', f'{video.id}-init-$RepresentationID$.mp4',  # Initialization segment name
            '-media_seg_name', f'{video.id}-chunk-$RepresentationID$-$Number%05d$.m4s',  # Media segment name
            '-adaptation_sets', 'id=0,streams=v id=1,streams=a',  # Adaptation sets for video and audio
            output_mpd_path
        ]

        # Execute the ffmpeg command
        subprocess.run(cmd, check=True, cwd=video_dir)

        # Update the database record with the new .mpd file path
        video.file.name = os.path.relpath(output_mpd_path, base_dir)
        video.save()

        # Optionally, delete the original video file
        os.remove(original_video_path)

        return "Conversion successful and original video removed."

    except Videos.DoesNotExist:
        return "Video not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"
