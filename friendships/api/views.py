from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate,
)
from friendships.models import HBaseFollowing, HBaseFollower, Friendship
from friendships.services import FriendshipService
from gatekeeper.models import GateKeeper
from ratelimit.decorators import ratelimit
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from utils.paginations import EndlessPagination


class FriendshipViewSet(viewsets.GenericViewSet):
    # POST /api/friendship/1/follow  go to follow user_id=1
    # queryset User.objects.all()
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()
    # different views need different pagination
    pagination_class = EndlessPagination

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def followers(self, request, pk):
        if GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            page = self.paginator.paginate_hbase(HBaseFollower, (pk,), request)
        else:
            friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
            page = self.paginate_queryset(friendships)

        serializer = FollowerSerializer(page, many=True, context={'request': request})
        return self.paginator.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def followings(self, request, pk):
        if GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            page = self.paginator.paginate_hbase(HBaseFollowing, (pk,), request)
        else:
            friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
            page = self.paginate_queryset(friendships)

        serializer = FollowingSerializer(page, many=True, context={'request': request})
        return self.paginator.get_paginated_response(serializer.data)


    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def follow(self, request, pk):
        # dup follow e.g. front end click follow many times
        # keep silent network delay, it is not a real error
        if FriendshipService.has_followed(request.user.id, int(pk)):
            return Response({
                'success': True,
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)
        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        #FriendshipService.invalidate_following_cache(request.user.id)
        return Response({'success': True}, status=status.HTTP_201_CREATED)


    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def unfollow(self, request, pk):
        unfollow_user = self.get_object()
        # pk type is str, need to convert type
        #if request.user.id == int(pk):
        # raise 404 if no user with id=pk
        if request.user.id == unfollow_user.id:
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        # return 2 values, 1st how many ele deleted totally
        # 2nd how many deleted each type
        #deleted, _ = Friendship.objects.filter(
        #    from_user=request.user,
        #    to_user=unfollow_user,
        #).delete()
        #FriendshipService.invalidate_following_cache(request.user.id)
        deleted = FriendshipService.unfollow(request.user.id, int(pk))
        return Response({
            'success': True,
            'deleted': deleted
        })

    def list(self, request):
        return Response({'message': 'this is friendship home page'})

