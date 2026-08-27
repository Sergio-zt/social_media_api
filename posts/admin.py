from django.contrib import admin
from posts.models import Post, Comment, ScheduledPostRequest
from posts.tasks import create_scheduled_post_task


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "content", "created_at")
    list_filter = ("created_at", "author")
    search_fields = ("content", "author__email")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post", "created_at")


@admin.register(ScheduledPostRequest)
class ScheduledPostRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "scheduled_time", "created_at")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            create_scheduled_post_task.apply_async(
                args=[obj.author.id, obj.content], eta=obj.scheduled_time
            )
