# about/test_about.py
from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse


class AboutTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tested_data = [
            {
                'url': '/about/author/',
                'status': HTTPStatus.OK,
                'name': reverse('about:author'),
                'template': 'about/author.html',
            },
            {
                'url': '/about/tech/',
                'status': HTTPStatus.OK,
                'name': reverse('about:tech'),
                'template': 'about/tech.html',
            },
        ]

    def test_url_responce_code(self):
        """Страницы, доступные пользователю."""
        for data in self.tested_data:
            with self.subTest(url=data['url']):
                response = self.client.get(data['url'])
                self.assertEqual(
                    response.status_code,
                    data['status'],
                    f'Неверный код ответа страницы '
                    f'{response.status_code}. Ожидается {data["status"]}'
                )

    def test_used_template(self):
        """Соответствие шаблонов адресам"""
        for data in self.tested_data:
            with self.subTest(template=data['template']):
                response = self.client.get(data['url'])
                self.assertTemplateUsed(
                    response,
                    data['template'],
                    f'Неверный шаблон для адреса {data["url"]}'
                )

    def test_used_names(self):
        """Соответствие шаблонов именам"""
        for data in self.tested_data:
            with self.subTest(template=data['template']):
                response = self.client.get(data['name'])
                self.assertTemplateUsed(
                    response,
                    data['template'],
                    f'Неверный шаблон для имени {data["name"]}'
                )
