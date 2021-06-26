from celery import shared_task
from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from utils.time_constants import ONE_HOUR


@shared_task(time_limit=ONE_HOUR)
def fanout_newsfeeds_task(tweet_id):
    # import to prevent cycle dependence
    from newsfeeds.services import NewsFeedService

    # wrong method, put DB operation in for
    #for follower in FriendshipService.get_followers(tweet.user):
    #    Newsfeed.objects.create(
    #        user=follower,
    #        tweet=tweet,
    #    )
    # right method
    tweet = Tweet.objects.get(id=tweet_id)
    newsfeeds = [
        NewsFeed(user=follower, tweet=tweet)
        for follower in FriendshipService.get_followers(tweet.user)
    ]
    newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
    NewsFeed.objects.bulk_create(newsfeeds)

    # bulk create won't trigger post_save signal, so push to cache manually
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)