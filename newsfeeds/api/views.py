from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.services import NewsFeedService
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from utils.paginations import EndlessPagination
from newsfeeds.models import NewsFeed


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def list(self, request):
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(request.user.id)
        page = self.paginator.paginate_cached_list(cached_newsfeeds, request)
        if page is None:
            queryset = NewsFeed.objects.filter(user=request.user)
            page = self.paginate_queryset(queryset)
        serializer = NewsFeedSerializer(
            page,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)
