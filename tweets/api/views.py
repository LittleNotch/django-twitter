from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetCreateSerializer
from tweets.models import Tweet

class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    """
    API endpoint that allows user to create, list tweets
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetCreateSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """
        overload list method, not list all tweets, user_id should be specified
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)
        # select * from twitter_tweets
        # where user_id = xxx
        # order by created_at desc
        # using user and created_at associated index
        # only user index is not good enough
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)
        # json response default use hash format
        # not list format
        return Response({'tweets': serializer.data})

    def create(self, reqeust, *args, **kwargs):
        """
        overload create method, need current logged in user as tweet.user
        :param reqeust:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = TweetCreateSerializer(
            data=reqeust.data,
            context={'request': reqeust},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'error': serializer.errors,
            }, status=400)
        tweet = serializer.save()
        return Response(TweetSerializer(tweet).data, status=201)