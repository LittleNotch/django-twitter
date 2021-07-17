from django.conf import settings
from django.core.cache import caches
from friendships.models import HBaseFollowing, HBaseFollower, Friendship
from gatekeeper.models import GateKeeper
from utils.redis_helper import RedisHelper
from twitter.cache import FOLLOWINGS_PATTERN

import time

cache = caches['testing'] if settings.TESTING else caches['default']


class FriendshipService(object):

    @classmethod
    def get_follower_ids(cls, to_user_id):
        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            friendships = Friendship.objects.filter(to_user_id=to_user_id)
        else:
            friendships = HBaseFollower.filter(prefix=(to_user_id, None))
        return [friendship.from_user_id for friendship in friendships]

    @classmethod
    def get_following_user_id_set(cls, from_user_id):
        # cache set in Redis
        name = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        user_id_set = RedisHelper.get_all_members_from_set(name)

        # cache hit, need to change b'123' -> 123
        if user_id_set is not None:
            user_id_set_new = set([])
            for user_id in user_id_set:
                if isinstance(user_id, bytes):
                    user_id = user_id.decode('utf-8')
                    user_id_set_new.add(int(user_id))
            return user_id_set_new

        # cache miss
        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            friendships = Friendship.objects.filter(from_user_id=from_user_id)
        else:
            friendships = HBaseFollowing.filter(prefix=(from_user_id, None))
        user_id_set = set([
            fs.to_user_id
            for fs in friendships
        ])

        # push in Redis
        RedisHelper.add_id_to_set(name, user_id_set)
        return user_id_set

    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        cache.delete(key)

    @classmethod
    def get_follow_instance(cls, from_user_id, to_user_id):
        followings = HBaseFollowing.filter(prefix=(from_user_id, None))
        for follow in followings:
            if follow.to_user_id == to_user_id:
                return follow
        return None

    @classmethod
    def has_followed(cls, from_user_id, to_user_id):
        if from_user_id == to_user_id:
            return False

        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            return Friendship.objects.filter(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
            ).exists()

        instance = cls.get_follow_instance(from_user_id, to_user_id)
        return instance is not None

    @classmethod
    def follow(cls, from_user_id, to_user_id):
        if from_user_id == to_user_id:
            return None

        # update Redis
        cls.add_following_id_in_redis(from_user_id, to_user_id)

        # update DB
        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            # create data in MySQL
            return Friendship.objects.create(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
            )

        # create data in hbase
        now = int(time.time() * 1000000)
        HBaseFollower.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            created_at=now,
        )
        return HBaseFollowing.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            created_at=now,
        )

    @classmethod
    def unfollow(cls, from_user_id, to_user_id):
        if from_user_id == to_user_id:
            return 0

        # update Redis
        cls.remove_following_id_in_redis(from_user_id, to_user_id)

        # update DB
        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            deleted, _ = Friendship.objects.filter(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
            ).delete()
            return deleted
        instance = cls.get_follow_instance(from_user_id, to_user_id)
        if instance is None:
            return 0

        HBaseFollowing.delete(from_user_id=from_user_id, created_at=instance.created_at)
        HBaseFollower.delete(to_user_id=to_user_id, created_at=instance.created_at)
        return 1

    @classmethod
    def get_following_count(cls, from_user_id):
        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            return Friendship.objects.filter(from_user_id=from_user_id).count()
        followings = HBaseFollowing.filter(prefix=(from_user_id, None))
        return len(followings)

    @classmethod
    def add_following_id_in_redis(cls, from_user_id, to_user_id):
        name = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        id_set = set([to_user_id])

        RedisHelper.add_id_to_set(name, id_set)


    @classmethod
    def remove_following_id_in_redis(cls, from_user_id, to_user_id):
        name = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        id_set = set([to_user_id])

        RedisHelper.remove_id_from_set(name, id_set)
