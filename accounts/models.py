from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    # One2One field will create an unique index，make sure
    # no multiple UserProfile points to one User
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    avatar = models.FileField(null=True)
    # when a user is created，will create an object of user profile
    # now user dont have to set up nickname and related info，so null=True
    nickname = models.CharField(null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.user, self.nickname)


# define property method in profile，inserting in User model
# Then when we access an object of user to profile = user_instance.profile
# will implement get_or_create in UserProfile to get related object
def get_profile(user):
    if hasattr(user, '_cached_user_profile'):
        return getattr(user, '_cached_user_profile')
    profile, _ = UserProfile.objects.get_or_create(user=user)
    # use user's object's property to cache，avoid activate same user's profile
    # for multiple time when accessing the database
    setattr(user, '_cached_user_profile', profile)
    return profile


# add profile's property to User Model to access faster
User.profile = property(get_profile)
