from newsfeeds.models import NewsFeed
from friendships.services import FriendshipService


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        # bad example #1
        # if DB operation in for is too slow
        #for follower in FriendshipService.get_followers(tweet.user):
        #    NewsFeed.objects.create(
        #        user=follower,
        #        tweet=tweet,
        #    )

        # use bulk_create, can combine insert to 1 SQL
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)