from accounts.listeners import profile_changed
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_delete
from utils.listeners import invalidate_object_cache


class UserProfile(models.Model):
    # One2one filed creates a unique index, avoid multi UserProfile -> User
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    # Django also has a ImageField, try not to use it, has more problems
    # FileField can do the same thing, eventually save in file format, use url to visit
    avatar = models.FileField(null=True)
    # when a user is created, a user profile also created
    # so user hasn't set nickname, so null=True
    nickname = models.CharField(null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.user, self.nickname)

# define a property method profile(), put into model User
# when user_instance.profile, UserProfile get_or_create to get profile object
# python benefit to hack, easy to get profile via User
def get_profile(user):
    # put import inside function to prevent cycling dependence
    from accounts.services import UserService

    if hasattr(user, '_cached_user_profile'):
        return getattr(user, '_cached_user_profile')
    profile = UserService.get_profile_through_cache(user.id)
    # cache User, avoid same user profile multi DB
    setattr(user, '_cached_user_profile', profile)
    return profile


# add profile property to User model for quick visit
User.profile = property(get_profile)

# hook up with listeners to invalidate cache
pre_delete.connect(invalidate_object_cache, sender=User)
post_save.connect(invalidate_object_cache, sender=User)

pre_delete.connect(profile_changed, sender=UserProfile)
post_save.connect(profile_changed, sender=UserProfile)
