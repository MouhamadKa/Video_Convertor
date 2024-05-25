from django.utils.deprecation import MiddlewareMixin

class DeviceDetectionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if 'mobile' in user_agent:
            request.device_type = 'mobile'
        elif 'tablet' in user_agent:
            request.device_type = 'tablet'
        else:
            request.device_type = 'desktop'