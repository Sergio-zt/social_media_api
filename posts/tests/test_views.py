from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from posts.models import Post

User = get_user_model()


class PostApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword123"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_post_success(self):
        """Success posting with authorized user"""
        payload = {"content": "Text of test post"}

        response = self.client.post("/api/content/posts/", payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().content, "Text of test post")

    def test_create_post_unauthenticated(self):
        """Unauthorized user can not create posts"""
        self.client.force_authenticate(user=None)

        payload = {"content": "Text of test post"}
        response = self.client.post("/api/content/posts/", payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
