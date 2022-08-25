from django.contrib.auth.models import User
from utils.time_helpers import utc_now
from django.contrib.contenttypes.models import ContentType
from django.db import models
from like.models import Like
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES
from tweets.listeners import push_tweet_to_cache
from django.db.models.signals import post_save
from utils.listeners import invalidate_object_cache
from utils.memcached_helper import MemcachedHelper

class Tweet(models.Model):
    #Who post the tweet
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    def __str__(self):
        # displays when executing print(tweet instance) -> tracking
        return f'{self.created_at} {self.user}: {self.content}'

    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)


class TweetPhoto(models.Model):
    # photo under which tweets
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)

    # who uploaded the photo
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    # file of photo
    file = models.FileField()
    order = models.IntegerField(default=0)

    # status of photo for audit
    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )

    # soft delete mark
    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at'),
            ('has_deleted', 'created_at'),
            ('status', 'created_at'),
            ('tweet', 'order'),
        )

    def __str__(self):
        return f'{self.tweet_id}: {self.file}'


post_save.connect(invalidate_object_cache, sender=Tweet)
post_save.connect(push_tweet_to_cache, sender=Tweet)