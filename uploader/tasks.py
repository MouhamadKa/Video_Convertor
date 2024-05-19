from django.conf import settings
import subprocess
import os
from celery import shared_task
from .models import Videos

@shared_task
def convert_video(video_id):
    try:
        video = Videos.objects.get(id=video_id)
        input_path = video.video_file.path
        base_output_dir = os.path.splitext(input_path)[0]  # Base directory for all output files

        resolutions = {
            "mobile": ("1280", "720"),
            "tablet": ("1920", "1080"),
            "desktop": ("2560", "1440")
        }

        for resolution, (width, height) in resolutions.items():
            output_dir = os.path.join(base_output_dir, resolution)
            os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

            mpd_filename = os.path.basename(output_dir) + ".mpd"
            output_mpd_path = os.path.join(output_dir, mpd_filename)

            command = [
                'ffmpeg',
                '-i', input_path,
                '-vf', f'scale={width}:-2',  # Ensure aspect ratio is maintained and height is divisible by 2
                '-map', '0',
                '-c:v', 'libx264',
                '-b:v', '3000k',  # Use a higher bitrate for better quality
                '-r', '30',
                '-g', '60',
                '-sc_threshold', '0',
                '-c:a', 'aac',
                '-b:a', '192k',  # Increase audio bitrate for better quality
                '-f', 'dash',
                '-init_seg_name', mpd_filename.replace('.mpd', '-init-$RepresentationID$.mp4'),
                '-media_seg_name', mpd_filename.replace('.mpd', '-chunk-$RepresentationID$-$Number%05d$.m4s'),
                output_mpd_path
            ]
            print(f"Size for {resolution}: {width, height}")

            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=output_dir)

            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)

        os.remove(input_path)  # Delete the original file

        # Update video model with new file path if needed
        relative_output_path = os.path.relpath(output_mpd_path, settings.MEDIA_ROOT)
        video.video_file.name = relative_output_path
        video.save()

    except Videos.DoesNotExist:
        print(f"Video with ID {video_id} does not exist.")
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed with error: {e.stderr}")
    except Exception as e:
        print(f"An error occurred: {e}")

            
