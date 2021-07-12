from celery import shared_task
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from inbox.services import NotificationService
from likes.models import Like
from tweets.models import Tweet
from utils.time_constants import ONE_HOUR


@shared_task(routing_key='likes', time_limit=ONE_HOUR)
def async_create_like_main_task(content_type_int, object_id, user_id):
    if content_type_int == 0:
        model_class = Comment
    else:
        model_class = Tweet

    # first get_or_create Like
    instance, created = Like.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(model_class),
        object_id=object_id,
        user_id=user_id,
    )

    # send notification
    if created:
        NotificationService.send_like_notification(instance)

    return '1 like created.'