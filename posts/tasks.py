from celery import shared_task
from django.contrib.auth import get_user_model
from posts.models import Post

User = get_user_model()


@shared_task
def create_scheduled_post_task(author_id, content):
    """
    Background task to create a post at a scheduled time.
    """
    try:
        user = User.objects.get(id=author_id)
        post = Post.objects.create(author=user, content=content)
        return f"Post {post.id} successfully created for user {user.email}"
    except User.DoesNotExist:
        return "Failed: User does not exist"
