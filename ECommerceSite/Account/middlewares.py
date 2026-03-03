from django.contrib import messages

class ProfileNotificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:

            if request.user.needs_profile_notification:
                msg = "Te rugam sa verifici Telefonul si Email-ul"
                messages.warning(request, msg)
                request.user.needs_profile_notification = False
                request.user.save(update_fields=['needs_profile_notification'])

        response = self.get_response(request)
        return response