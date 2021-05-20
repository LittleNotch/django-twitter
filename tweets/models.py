from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from likes.models import Like
from utils.time_helpers import utc_now
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES


# Create your models here.
class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    def __str__(self):
        # print(tweet instance) display following
        return f'{self.created_at} {self.user}: {self.content}'

    @property
    def hours_to_now(self):
        #datetime.now need to add utc time zone
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')


class TweetPhoto(models.Model):
    # photo associated with tweet
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)

    # who upload this photo, from tweet can get this, denormalize, put it in photo
    # a user has history, his new photos maybe high risk, or forbid all photos of a user
    # can use this to filter
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # photo file
    file = models.FileField()
    order = models.IntegerField(default=0)

    # photo status
    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )

    # soft delete mark as deleted, after a while, remove it, use asynchronous
    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at'),
            ('has_deleted', 'created_at'),
            ('status', 'created_at'),
            ('tweet', 'order'),
        )

    def __str__(self):
        return f'{self.tweet_id}: {self.file}'