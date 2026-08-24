from rest_framework import viewsets, permissions, filters, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating, reading, updating, and deleting posts.
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    # Enables search by hashtag (or any word) in the content field
    # Example usage: /api/posts/?search=#coffie
    filter_backends = [filters.SearchFilter]
    search_fields = ["content"]

    def perform_create(self, serializer):
        """Automatically set the current user as the author of the post."""
        serializer.save(author=self.request.user)

    @action(detail=False, methods=["get"])
    def feed(self, request):
        """
        Endpoint to retrieve posts from the current user and users they follow.
        """
        user = request.user

        # Get IDs of all users the current user is following
        following_ids = user.following_links.values_list("following_id", flat=True)

        # Get posts where author is in following_ids OR author is the current user
        # .distinct() ensures we don't get duplicate posts
        posts = Post.objects.filter(
            Q(author_id__in=following_ids) | Q(author=user)
        ).distinct()

        # Apply pagination (standard DRF feature)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        """Endpoint to like a specific post."""
        post = self.get_object()
        post.likes.add(request.user)
        return Response(
            {"detail": "Post liked successfully."}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def unlike(self, request, pk=None):
        """Endpoint to unlike a specific post."""
        post = self.get_object()
        post.likes.remove(request.user)
        return Response(
            {"detail": "Post unliked successfully."}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"])
    def liked(self, request):
        """Endpoint to list all posts liked by the current user."""
        posts = Post.objects.filter(likes=request.user)

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_comment(self, request, pk=None):
        """Endpoint to add a comment to a specific post."""
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            # Pass the author and post objects directly to bypass read-only fields
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(
    mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    """
    ViewSet strictly for updating and deleting comments.
    (Creating comments is handled in the PostViewSet's add_comment action).
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
