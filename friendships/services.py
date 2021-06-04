from friendships.models import Friendship


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
    def has_followed(cls, from_user, to_user):
        return Friendship.objects.filter(
            from_user=from_user,
            to_user=to_user,
        ).exists()