from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from utils.paginations import EndlessPagination


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def get_queryset(self):
        # self-define queryset, because newsfeed need logged in
        # use is current user can get newsfeed
        return NewsFeed.objects.filter(user=self.request.user)

    def list(self, request):
        queryset = self.paginate_queryset(self.get_queryset())
        serializer = NewsFeedSerializer(
            queryset,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)