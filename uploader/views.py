from django.http import JsonResponse
from django.views.generic.base import TemplateView
from chunked_upload.views import ChunkedUploadView, ChunkedUploadCompleteView
from django.shortcuts import get_object_or_404, render
from .models import MyChunkedUpload, Videos
from .tasks import convert_video

class ChunkedUploadDemo(TemplateView):
    template_name = 'chunked_upload_demo.html'

class MyChunkedUploadView(ChunkedUploadView):
    model = MyChunkedUpload
    field_name = 'the_file'

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        pass

class MyChunkedUploadCompleteView(ChunkedUploadCompleteView):
    model = MyChunkedUpload

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        pass

    def on_completion(self, uploaded_file, request):
        # Do something with the uploaded file.
        vid = Videos.objects.create(video_file=uploaded_file)
        vid.save()

        # Trigger the Celery task to convert the video
        convert_video(vid.id)

def home_page(request):
    videos = Videos.objects.all()
    video_data = []
    for video in videos:
        original_video_name = video.video_file.name.split('/')[-1].split('.')[0]
        video_data.append({
            'id': video.id,
            'video_file_url': video.video_file.url,
            'download_urls': {
                'mobile': f"/media/post_videos/{original_video_name}/mobile/{original_video_name}_mobile.mp4",
                'tablet': f"/media/post_videos/{original_video_name}/tablet/{original_video_name}_tablet.mp4",
                'desktop': f"/media/post_videos/{original_video_name}/desktop/{original_video_name}_desktop.mp4",
            }
        })
    return render(request, 'home_page.html', {'videos': video_data})


def get_video(request, video_id):
    video = get_object_or_404(Videos, id=video_id)
    device_type = getattr(request, 'device_type', 'desktop')

    base_url = video.video_file.url.split('post_videos/')[0] + 'post_videos'
    original_video_name = video.video_file.name.split('/')[-1].split('.')[0]
    mp4_url = f"{base_url}/mobile/{original_video_name}" + '.mp4'
    
    response_data = {
        'id': video.id,
        'video_url': {
            'mobile': f"{base_url}/mobile/{original_video_name}/mobile.mpd",
            'tablet': f"{base_url}/tablet/{original_video_name}/tablet.mpd",
            'desktop': f"{base_url}/desktop/{original_video_name}/desktop.mpd",
        },
        'download_urls': {
            'url': mp4_url,
        }
    }
    return JsonResponse(response_data)

