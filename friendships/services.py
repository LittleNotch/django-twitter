from django.conf import settings
from django.core.cache import caches
from friendships.models import Friendship
from twitter.cache import FOLLOWINGS_PATTERN

cache = caches['testing'] if settings.TESTING else caches['default']


class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        # bad example  #1
        # n + 1 queries
        # filter all friendships, 1 query
        # for each friendship get from_user, N queries
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]

        # bad example #2
        # use join, too slow
        #friendships = Friendship.objects.filter(
        #    to_user=user
        #).select_related('from_user')
        #return [friendship.from_user for friendship in friendships]

        # good example #1 filter id
        #friendships = Friendship.objects.filter(to_user=user)
        #follower_ids = [friendship.from_user_id for friendship in friendships]
        #followers = User.objects.filter(id_in=follower_ids)

        # prefetch_related, in Query, generate 2 SQL
        friendships = Friendship.objects.filter(
            to_user=user
        ).prefetch_related('from_user')
        return[friendship.from_user for friendship in friendships]

    @classmethod
    def get_follower_ids(cls, to_user_id):
        friendships = Friendship.objects.filter(to_user_id=to_user_id)
        return [friendship.from_user_id for friendship in friendships]

    @classmethod
    def get_following_user_id_set(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        user_id_set = cache.get(key)
        if user_id_set is not None:
            return user_id_set

        friendships = Friendship.objects.filter(from_user_id=from_user_id)
        user_id_set = set([
            fs.to_user_id
            for fs in friendships
        ])
        cache.set(key, user_id_set)
        return user_id_set

    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        cache.delete(key)