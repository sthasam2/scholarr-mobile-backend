import random
import string

from django.test import TestCase

from apps.users.models import CustomUser


class UserProfileTest(TestCase):
    def random_string(self):
        return "".join(random.choice(string.ascii_lowercase) for i in range(10))

    def test_user_has_profile(self):
        user = CustomUser(
            email=f"{self.random_string()}@{self.random_string()}.com",
            username=self.random_string(),
            password="123ajkdsa34fana",
        )
        user.save()

        self.assertTrue(hasattr(user, "profile"))


class UpdateUserTest(TestCase):
    def random_string(self):
        return "".join(random.choice(string.ascii_lowercase) for i in range(10))

    def test_user_update(self):
        user = CustomUser(
            email=f"{self.random_string()}@{self.random_string()}.com",
            username=self.random_string(),
            password="123ajkdsa34fana",
        )
        user.save()

        saved = CustomUser.objects.update_user(
            user.id,
            username="sambeg",
            password="new_password",
            email="sthas@dasd.com",
            active=False,
        )

        self.assertTrue(getattr(saved, "username") == "sambeg")
        self.assertTrue(saved.check_password("new_password"))
        self.assertTrue(getattr(saved, "email") == "sthas@dasd.com")
        self.assertTrue(getattr(saved, "active") == False)
