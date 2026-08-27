from unittest.mock import patch
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from posts.models import Post
from posts.tasks import create_scheduled_post_task

User = get_user_model()


class ScheduledPostApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test_celery@example.com", password="testpassword123"
        )
        self.client.force_authenticate(user=self.user)
        self.schedule_url = "/api/content/posts/schedule/"

    @patch('posts.views.create_scheduled_post_task.apply_async')
    def test_schedule_post_endpoint(self, mock_task):
        """The endpoint successfully accepts the payload and calls the Celery task"""
        payload = {
            "content": "This post should be scheduled via Celery",
            "scheduled_time": "2026-12-31T23:59:00Z",
        }

        response = self.client.post(self.schedule_url, payload)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("successfully scheduled", str(response.data))

        self.assertTrue(mock_task.called)

    def test_celery_task_execution(self):
        """The Celery task function successfully creates a Post in the database"""

        result = create_scheduled_post_task(self.user.id, "Executed directly in test")

        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().content, "Executed directly in test")
        self.assertIn("successfully created", result)
