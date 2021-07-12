from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from likes.api.serializers import (
    LikeSerializer,
    LikeSerializerForCancel,
    LikeSerializerForCreate,
)
from likes.models import Like
from likes.services import LikeService
from ratelimit.decorators import ratelimit
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from tweets.models import Tweet
from utils.decorators import required_params


class LikeViewSet(viewsets.GenericViewSet):
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializerForCreate

    @required_params(method='POST', params=['content_type', 'object_id'])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def create(self, request, *args, **kwargs):
        serializer = LikeSerializerForCreate(
            data=request.data,
            context={'request':request}
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        #instance, created = serializer.get_or_create()
        #if created:
        #    NotificationService.send_like_notification(instance)
        # use Message Queue to create Like in DB
        if serializer.validated_data['content_type'] == 'comment':
            content_type_int = 0
            model_class = Comment
        else:
            content_type_int = 1
            model_class = Tweet
        object_id = serializer.validated_data['object_id']
        LikeService.async_create_like(content_type_int, object_id, request.user.id)

        instance = Like(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=object_id,
            user=request.user,
        )

        return Response(
            LikeSerializer(instance).data,
            status=status.HTTP_201_CREATED,
        )
    @action(methods=['POST'], detail=False)
    @required_params(method='POST', params=['content_type', 'object_id'])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def cancel(self, request, *args, **kwargs):
        serializer = LikeSerializerForCancel(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.cancel()
        return Response(
            {
                'success': True
            }, status=status.HTTP_200_OK)