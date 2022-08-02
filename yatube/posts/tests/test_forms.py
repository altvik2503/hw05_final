# posts/tests/test_forms.py
from posts.models import Post
from django.test import override_settings
from posts.tests.test_data import (
    DataTestCase,
    TestPost,
    PostFormData,
    TEMP_MEDIA_ROOT,
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(DataTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_new_post(self):
        """Проверка создания новой записи из формы"""
        records_number_before = Post.objects.count()
        new_post = TestPost(
            text=self.fake.text(),
            author=self.authorized_user.id,
            group=self.group.id,
            image=self.image,
        )._asdict()
        response = self.authorized_client.post(
            self.url_create.url,
            data=new_post,
            follow=True,
        )
        new_post.pop('image')
        with self.subTest():
            self.assertRedirects(response, self.url_auth.url)
            self.assertEqual(records_number_before + 1, Post.objects.count())
            posts = Post.objects.filter(**new_post)
            self.assertEqual(posts.count(), 1)

    def test_edit_post_authorized(self):
        """Проверка изменения существующей записи в форме
        авторизованным пользователем
        """
        tested_post = Post.objects.create(**self.test_post._asdict())
        url = self.url_edit.get_url_with_id(tested_post.id)

        changed_form_data = PostFormData(
            text=self.fake.text(),
            group=self.group2.id,
            image=self.image2,
        )

        self.authorized_client.post(
            url,
            data = changed_form_data._asdict(),
            follow=True,
        )

        tested_post.refresh_from_db()

        tested_data = (
            (changed_form_data.text, tested_post.text),
            (changed_form_data.group, tested_post.group.id),
            (f'posts/{changed_form_data.image.name}', tested_post.image.name),
        )
        for expected, tested in tested_data:
            with self.subTest(field=tested):
                self.assertEqual(tested, expected)

    def test_edit_post_unauthorized(self):
        """Проверка отказа в изменениях неавторизованному пользователю"""
        tested_post = Post.objects.create(**self.test_post._asdict())
        url = self.url_edit.get_url_with_id(tested_post.id)

        changed_form_data = PostFormData(
            text=self.fake.text(),
            group=self.group2.id,
            image=self.image2,
        )

        self.client.post(
            url,
            data = changed_form_data._asdict(),
            follow=True,
        )

        tested_post.refresh_from_db()

        tested_data = (
            (self.test_post.text, tested_post.text),
            (self.test_post.group, tested_post.group),
        )
        for expected, tested in tested_data:
            with self.subTest(field=tested):
                self.assertEqual(tested, expected)
