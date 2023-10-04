from django.contrib.auth.signals import user_logged_out
from django.contrib.sessions.models import Session
from .models import UserActivity
from .utils import track_user_activity


class LogoutTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Check if the user has logged out
        if request.user.is_authenticated is False and request.session.session_key:
            session_key = request.session.session_key

            # Check if the session_key is valid and active
            try:
                session = Session.objects.get(session_key=session_key)
            except Session.DoesNotExist:
                pass
            else:
                if not session.get_decoded().get('_auth_user_id'):
                    # This session is associated with a logged-out user
                    user_activity_message = 'Logout'
                    UserActivity.objects.create(
                        user=None,  # No user is associated with the logout action
                        action=user_activity_message,
                        session_key=session_key
                    )

        return response


def user_logged_out_handler(sender, request, **kwargs):
    track_user_activity(request.user, 'Logout', 'Logout')


# Connect the user_logged_out signal to the user_logged_out_handler function
user_logged_out.connect(user_logged_out_handler)
