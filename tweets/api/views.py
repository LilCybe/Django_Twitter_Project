from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetCreateSerializer
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService

class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):

    #API endpoint that allows users to create, list tweets
    queryset = Tweet.objects.all()
    serializer_class = TweetCreateSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):

        #reload list method，not listing all tweets，must use user_id as criteria
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)

        # select * from twitter_tweets
        # where user_id = xxx
        # order by created_at desc
        tweets = Tweet.objects.filter(
            user_id = request.query_params['user_id']
        ).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)

        return Response({'tweets': serializer.data})

    def create(self, request):

        #reload create method，requiring the loging user to be tweet.user
        serializer = TweetCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet).data, status=201)
