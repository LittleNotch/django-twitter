from comments.api.permissions import IsObjectOwner
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from comments.models import Comment
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from utils.decorators import required_params



class CommentViewSet(viewsets.GenericViewSet):
    """
    implement lis, create, update, destroy
    no implement retrieve (single comment)
    """
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',)

    def get_permissions(self):
        # AllowAny() / IsAuthenticated() generate an object instance
        # not AllowAny / IsAuthenticated, this is just a class name
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['destroy', 'update']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    @required_params(params=['tweet_id'])
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        comments = self.filter_queryset(queryset).order_by('created_at')
        serializer = CommentSerializer(
            comments,
            context={'request': request},
            many=True,
        )
        return Response(
            {'comments': serializer.data},
            status=status.HTTP_200_OK
        )


    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        # must 'data=' specify param is to data
        # default first param is instance
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        # save method will trigger create()
        comment = serializer.save()
        return Response(
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        # get_object is DRF wrapped method, raise 404 error when cannot find
        serializer = CommentSerializerForUpdate(
            instance=self.get_object(),
            data=request.data,
        )
        if not serializer.is_valid():
            raise Response({
                'message': 'Please check input.'
            }, status=status.HTTP_400_BAD_REQUEST)
        # save() will trigger update()
        # save() depends on instance has param or not to decide create() or update()
        comment = serializer.save()
        return Response(
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        # DRF default return code 204 no content
        # return success=True to frontend 200 is more clear
        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)
