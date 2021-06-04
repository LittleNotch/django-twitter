def friendship_changed(sender, instance, **kwargs):
    # put import inside function to prevent cycling dependence
    from friendships.services import FriendshipService
    FriendshipService.invalidate_following_cache(instance.from_user_id)