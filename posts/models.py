from django.db import models
from django.conf import settings


class Post(models.Model):
    """
    Model representing a user's post.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    content = models.TextField()
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]  # Newest posts first

    def __str__(self):
        return f"Post {self.id} by {self.author.email}"


class Comment(models.Model):
    """
    Model representing a comment on a specific post.
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment {self.id} by {self.author.email} on Post {self.post.id}"


from django.conf import settings


class ScheduledPostRequest(models.Model):
    """
    Model for configure scheduled posts from admin.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Author"
    )
    content = models.TextField(verbose_name="Post text")
    scheduled_time = models.DateTimeField(verbose_name="Post time")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Scheduled post (Celery)"
        verbose_name_plural = "Scheduled posts (Celery)"

    def __str__(self):
        return f"Scheduled for {self.author} at {self.scheduled_time}"
