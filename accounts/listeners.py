def profile_changed(sender, instance, **kwargs):
    # import inside a function to prevent cycling dependence
    from accounts.services import UserService
    UserService.invalidate_profile(instance.user_id)