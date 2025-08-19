from itertools import count

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson, Subscription
from users.models import User


class CourseTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="test@test.com")
        self.course = Course.objects.create(
            name="Course 1", description="This is course number 1", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            name="Lesson 1",
            description="This is lesson number 1",
            course=self.course,
            owner=self.user,
        )
        self.client.force_authenticate(user=self.user)

    def test_course_retrieve(self):
        url = reverse("lms:course-detail", args=(self.course.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.course.name)

    def test_course_create(self):
        url = reverse("lms:course-list")
        data = {"name": "Test course 1", "description": "Test course 1"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.all().count(), 2)

    def test_course_update(self):
        url = reverse("lms:course-detail", args=(self.course.pk,))
        data = {"name": "Test course number 1"}
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), "Test course number 1")

    def test_course_delete(self):
        url = reverse("lms:course-detail", args=(self.course.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.all().count(), 0)

    def test_course_list(self):
        url = reverse("lms:course-list")
        response = self.client.get(url)
        data = response.json()
        result = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.course.pk,
                    "lesson_count": 1,
                    "is_subscribed": False,
                    "lessons": [
                        {
                            "id": self.lesson.pk,
                            "video_url": None,
                            "name": self.lesson.name,
                            "description": self.lesson.description,
                            "preview_image": None,
                            "course": self.course.pk,
                            "owner": self.user.pk,
                        }
                    ],
                    "name": self.course.name,
                    "description": self.course.description,
                    "preview_image": None,
                    "owner": self.user.pk,
                }
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)


class LessonTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="test@test.com")
        self.course = Course.objects.create(
            name="Course 1", description="This is course number 1", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            name="Lesson 1",
            description="This is lesson number 1",
            course=self.course,
            owner=self.user,
        )
        self.client.force_authenticate(user=self.user)

    def test_lesson_retrieve(self):
        url = reverse("lms:lessons_retrieve", args=(self.lesson.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.lesson.name)

    def test_lesson_create(self):
        url = reverse("lms:lessons_create")
        data = {"name": "Lesson 2", "description": "This is lesson number 2"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.all().count(), 2)

    def test_lesson_update(self):
        url = reverse("lms:lessons_update", args=(self.lesson.pk,))
        data = {"name": "Test les number 1"}
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), "Test les number 1")

    def test_lesson_delete(self):
        url = reverse("lms:lessons_delete", args=(self.lesson.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.all().count(), 0)

    def test_lesson_list(self):
        url = reverse("lms:lessons_list")
        response = self.client.get(url)
        data = response.json()
        result = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.lesson.pk,
                    "video_url": None,
                    "name": self.lesson.name,
                    "description": self.lesson.description,
                    "preview_image": None,
                    "course": self.lesson.course.pk,
                    "owner": self.user.pk,
                }
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)


class SubscriptionTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="test@test.com")
        self.course = Course.objects.create(
            name="Course 1", description="This is course number 1", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            name="Lesson 1",
            description="This is lesson number 1",
            course=self.course,
            owner=self.user,
        )
        self.client.force_authenticate(user=self.user)

    def test_subscribe_to_course(self):
        # Проверяем, что в начале пользователь не подписан на курс
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

        # Подписка на курс
        response = self.client.post(reverse("lms:subscription"), {"id": self.course.pk})

        # Проверяем, что подписка успешно добавлена
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe_from_course(self):
        # Сначала подписываем пользователя на курс
        Subscription.objects.create(user=self.user, course=self.course)

        # Проверяем, что подписка существует
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

        # Отмена подписки
        response = self.client.post(reverse("lms:subscription"), {"id": self.course.pk})

        # Проверяем, что подписка успешно удалена
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscribe_twice(self):
        # Подписываемся на курс
        Subscription.objects.create(user=self.user, course=self.course)

        # Пытаемся подписаться на тот же курс снова
        response = self.client.post(reverse("lms:subscription"), {"id": self.course.pk})

        # Проверяем, что сообщение об ошибке не возвращается
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"], "Подписка удалена"
        )  # Проверка, что действие верно

    def test_unsuscribe_non_existent(self):
        # Проверка, что пользователь не может отписаться от несуществующей подписки
        response = self.client.post(reverse("lms:subscription"), {"id": self.course.pk})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"], "Подписка добавлена"
        )  # Проверяем, что создана новая подписка
