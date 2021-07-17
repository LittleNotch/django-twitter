from .tweet import Tweet
from django.contrib.auth.models import User
from django.db import models
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES


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
