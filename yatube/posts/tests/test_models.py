# posts/tests/test_models.py
from posts.tests.test_data import DataTestCase


class PostModelTest(DataTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_models_have_correct_labels(self):
        """Проверка корректности работы функции __str__,
        заголовков и строк подсказки моделей.
        """
        post = self.post
        group = self.group
        post_field = post._meta.get_field('text')
        group_field = group._meta.get_field('title')
        tested_objects = (
            (str(post), post.text[:15]),
            (str(group), group.title),
            (post_field.verbose_name, 'Текст поста'),
            (group_field.verbose_name, 'Группа'),
            (post_field.help_text, 'Введите текст поста'),
            (group_field.help_text, 'Группа, к которой будет относиться пост'),
        )
        for value, excepted in tested_objects:
            with self.subTest(value=value, excepted=excepted):
                self.assertEqual(value, excepted)
