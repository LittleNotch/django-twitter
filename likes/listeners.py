from utils.redis_helper import RedisHelper


def incr_likes_count(sender, instance, created, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        # TODO do similar operations for Comment
        return

    # Don't use tweet.likes_count += 1; tweet.save()
    # not atomic, must use "update"
    tweet = instance.content_object
    Tweet.objects.filter(id=tweet.id).update(likes_count=F('likes_count') + 1)
    RedisHelper.incr_count(tweet, 'likes_count')


def decr_likes_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        # TODO do similar operations for Comment
        return

    # handle tweet likes cancel
    tweet = instance.content_object
    Tweet.objects.filter(id=tweet.id).update(likes_count=F('likes_count') - 1)
    RedisHelper.decr_count(tweet, 'likes_count')