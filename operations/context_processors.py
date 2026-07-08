from .models import Notification

def notification_context(request):
    if request.user.is_authenticated:
        # We use .filter().count() to keep it efficient
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_count': count}
    return {'unread_count': 0}