from rest_framework import serializers
from .models import Post, Comment


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model.
    """

    author_email = serializers.ReadOnlyField(source="author.email")

    class Meta:
        model = Comment
        fields = [
            "id",
            "author",
            "author_email",
            "post",
            "text",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "post", "created_at", "updated_at"]


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model.
    """

    author_email = serializers.ReadOnlyField(source="author.email")

    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "author_email",
            "content",
            "image",
            "likes_count",
            "is_liked",
            "comments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]

    def get_likes_count(self, obj):
        """Returns the total number of likes for the post."""
        return obj.likes.count()

    def get_is_liked(self, obj):
        """
        Checks if the current authenticated user has liked this post.
        Requires 'request' to be passed in the serializer context.
        """
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
