# posts/tests/test_urls.py
from django.test import override_settings
from http import HTTPStatus
from posts.tests.test_data import DataTestCase, TEMP_MEDIA_ROOT


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostURLTests(DataTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.urls_available_all_clients = (
            cls.url_main_page,
            cls.url_group,
            cls.url_auth,
            cls.url_detail,
        )
        cls.urls_available_authorized_clients = (
            cls.url_create,
            cls.url_edit,
        )
        cls.urls_matches_template = (
            cls.url_main_page,
            cls.url_group,
            cls.url_auth,
            cls.url_detail,
            cls.url_create,
            cls.url_edit,
            cls.url_follow_list,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_page_available_all_clients(self):
        """Проверка страниц, доступных пользователю."""
        for test_url in self.urls_available_all_clients:
            url = test_url.get_url_with_id(self.post.id)
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

    def test_page_available_authorized_clients(self):
        """Проверка страниц, доступных авторизованному пользователю."""
        for test_url in self.urls_available_authorized_clients:
            url = test_url.get_url_with_id(self.post.id)
            with self.subTest(url=url):
                response = self.authorized_client.get(url).status_code
                self.assertEqual(
                    response,
                    HTTPStatus.OK
                )
                self.assertNotEqual(
                    self.client.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_url_redirect_page(self):
        """Проверка страниц, недоступных неавторизованному пользователю."""
        urls_for_redirect = (
            (self.url_create.url, '/?next=/create/'),
            (
                self.url_edit.get_url_with_id(self.post.id),
                '/?next=' + self.url_edit.get_url_with_id(self.post.id)
            ),
        )
        for url, redirect in urls_for_redirect:
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_used_template(self):
        """Проверка названий используемых шаблонов."""
        for test_url in self.urls_matches_template:
            template = test_url.template
            url = test_url.get_url_with_id(self.post.id)
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
