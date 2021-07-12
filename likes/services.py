from likes.models import Like
from likes.tasks import async_create_like_main_task
from django.contrib.contenttypes.models import ContentType

class LikeService(object):

    @classmethod
    def has_liked(cls, user, target):
        if user.is_anonymous:
            return False
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user,
        ).exists()

    @classmethod
    def async_create_like(cls, content_type_int, object_id, user_id):
        # message queue create a task (param = like instance)
        # any worker can get this task
        # worker will run async_create_like_task
        # create a task only, celery does not know how to serialize an object
        async_create_like_main_task.delay(content_type_int, object_id, user_id)