from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now

class Tweet(models.Model):
    #Who post the tweet
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

    def __str__(self):
        # displays when executing print(tweet instance) -> tracking
        return f'{self.created_at} {self.user}: {self.content}'
