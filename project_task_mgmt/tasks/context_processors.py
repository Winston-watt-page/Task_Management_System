"""
Context processors for tasks app
"""
from tasks.models import Notification


def notifications_processor(request):
    """
    Add unread notifications count to all templates
    """
    context = {}
    if request.user.is_authenticated:
        context['unread_notifications_count'] = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        context['recent_notifications'] = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
    else:
        context['unread_notifications_count'] = 0
        context['recent_notifications'] = []
    
    return context
