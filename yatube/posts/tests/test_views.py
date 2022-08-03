# posts/tests/test_views.py
from django.core.cache import cache
from collections import namedtuple
from django import forms

from posts.models import Post, Follow, Comment
from posts.tests.test_data import (
    DataTestCase,
    FakePaginator,
    PostFormFieldsTypes,
    TestPost,
)


class PostViewTests(DataTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.FORM_CREATE_POST_TITLE = 'Новый пост'
        cls.FORM_EDIT_POST_TITLE = 'Редактировать пост'

        # Create tests lists
        cls.expected_form_fields_types = PostFormFieldsTypes(
            text=forms.fields.CharField,
            group=forms.fields.ChoiceField,
            image=forms.fields.ImageField,
        )
        cls.urls_matches_name = (
            cls.url_main_page,
            cls.url_group,
            cls.url_auth,
            cls.url_detail,
            cls.url_create,
            cls.url_edit,
            cls.url_follow_list,
        )
        cls.urls_form_fields_types = (
            cls.url_create,
            cls.url_edit,
        )
        cls.urls_context_content = (
            cls.url_main_page,
            cls.url_group,
            cls.url_auth,
        )

        # Create tests posts
        test_posts_1 = TestPost(
            text=cls.fake.text(),
            author=cls.author.id,
            group=cls.group.id,
            image=cls.image2,
        )
        test_posts_2 = TestPost(
            text=cls.fake.text(),
            author=cls.author2.id,
            group=cls.group2.id,
            image=cls.image2,
        )
        test_posts_3 = TestPost(
            text=cls.fake.text(),
            author=cls.author2.id,
            group=cls.group.id,
            image=cls.image,
        )
        test_posts = (
            (test_posts_1, 11),
            (test_posts_2, 2,),
            (test_posts_3, 5),
        )
        range_from, range_to = 0, 0
        for test_post, number in test_posts:
            range_to += number
            Post.objects.bulk_create([(Post(
                text=test_post.text + str(i),
                author_id=test_post.author,
                group_id=test_post.group,
            )) for i in range(range_from, range_to)])
            range_from += number

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_used_names(self):
        """Проверка соответствия шаблонов именам."""
        for test_url in self.urls_matches_name:
            url = test_url.get_url_from_name(self.post.id)
            template = test_url.template
            with self.subTest(template=template, name=test_url.name):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_context_fields_types_create_edit(self):
        """Проверка соответствия типов полей контекста
        форм создания и редактирования поста.
        """
        for tested_url in self.urls_form_fields_types:
            url = tested_url.get_url_with_id(self.post.id)
            response = self.authorized_client.get(url)
            form = response.context.get('form')
            form_fields = self.expected_form_fields_types._asdict()
            for tested, expected in form_fields.items():
                form_field = form.fields.get(tested)
                with self.subTest(url=url):
                    self.assertIsInstance(form_field, expected)

    def test_posts_list_pages_show_correct_context(self):
        """Проверка содержимого контекстов списка постов шаблонов
        index.html, group_list.html, profile.html.
        """
        expected_post = Post.objects.create(**self.test_post._asdict())
        for tested_url in self.urls_context_content:
            url = tested_url.url
            response = self.authorized_client.get(url)
            tested_post = response.context['page_obj'][0]
            with self.subTest(url=url):
                self.assertEqual(tested_post, expected_post)

    def test_post_detail_page_show_correct_context(self):
        """Проверка содержимого контекста шаблона post_detail.html."""
        expected_post = self.post
        url = (
            self.url_detail.get_url_with_id(expected_post.id)
        )
        response = self.authorized_client.get(url)
        tested_post = response.context['post']
        with self.subTest(url=url):
            self.assertEqual(tested_post, expected_post)

    def test_post_edit_page_show_correct_context(self):
        """Проверка содержимого контекста шаблона при редактировании поста."""
        expected_post = self.post
        url = self.url_edit.get_url_with_id(expected_post.id)
        with self.subTest(url=url):
            response = self.authorized_client.get(url)
            form = response.context['form']
            self.assertEqual(form.initial['text'], expected_post.text)
            self.assertEqual(response.context['is_edit'], True)
            self.assertEqual(form.initial['group'], expected_post.group.id)
            self.assertEqual(
                response.context['title'],
                self.FORM_EDIT_POST_TITLE
            )

    def test_post_create_page_show_correct_context(self):
        """Проверка содержимого контекста шаблона при создании поста."""
        url = self.url_create.url
        response = self.authorized_client.get(url)
        post = response.context['form']
        with self.subTest(url=url):
            self.assertEqual(len(post.initial), 0)
            self.assertEqual(
                response.context['title'],
                self.FORM_CREATE_POST_TITLE
            )

    def test_paginator_pages_contains_right_number_records(self):
        """Паджинатор возвращает по 10 строк и остаток"""
        PostsNumber = namedtuple(
            'PostsNumber',
            (
                'test_url',
                'expected_number'
            )
        )
        urls_paginator = (
            PostsNumber(
                test_url=self.url_main_page,
                expected_number=Post.objects.count(),
            ),
            PostsNumber(
                test_url=self.url_group,
                expected_number=Post.objects.filter(
                    group=self.group
                ).count()
            ),
            PostsNumber(
                test_url=self.url_auth,
                expected_number=Post.objects.filter(
                    author=self.author
                ).count()
            ),
        )

        for tested_data in urls_paginator:
            paginator = FakePaginator(tested_data.expected_number)
            last_page_number = paginator.records_in_last_page()
            url_page_first = tested_data.test_url.url
            url_page_last = (
                tested_data.test_url.get_last_page_url(paginator.pages())
            )
            tested_pages = (
                (url_page_first, paginator.records_per_page),
                (url_page_last, last_page_number),
            )
            for url, number in tested_pages:
                with self.subTest(url=url):
                    cache.clear()
                    response = self.authorized_client.get(url)
                    self.assertEqual(
                        len(response.context.get('page_obj')), number
                    )

    def test_grop_post_added(self):
        """Пост с группой попал на начальную страницу,
        страницу только своей группы и в профайл
        """
        PostsDifference = namedtuple(
            'PostsDifference',
            (
                'tested_url',
                'number_before_add',
                'expected_difference'
            )
        )
        # Before post adding
        # Main page
        post_number = Post.objects.count()
        paginator = FakePaginator(post_number)
        main_page_data = PostsDifference(
            tested_url=self.url_main_page.get_last_page_url(
                paginator.pages()
            ),
            number_before_add=paginator.records_in_last_page(),
            expected_difference=1,
        )
        # Group
        post_number = Post.objects.filter(group=self.group).count()
        paginator = FakePaginator(post_number)
        group_page_data = PostsDifference(
            tested_url=self.url_group.get_last_page_url(
                paginator.pages()
            ),
            number_before_add=paginator.records_in_last_page(),
            expected_difference=1,
        )
        # Another group
        post_number = Post.objects.filter(group=self.group2).count()
        paginator = FakePaginator(post_number)
        another_group_page_data = PostsDifference(
            tested_url=self.url_group2.get_last_page_url(
                paginator.pages()
            ),
            number_before_add=paginator.records_in_last_page(),
            expected_difference=0,
        )
        # Author
        post_number = Post.objects.filter(author=self.author).count()
        paginator = FakePaginator(post_number)
        author_page_data = PostsDifference(
            tested_url=self.url_auth.get_last_page_url(
                paginator.pages()
            ),
            number_before_add=paginator.records_in_last_page(),
            expected_difference=1,
        )
        # Add post
        Post.objects.create(
            text='Any',
            author=self.author,
            group=self.group
        )
        # After post adding
        tested_data = (
            (
                main_page_data,
                Post.objects.count()
            ),
            (
                group_page_data,
                Post.objects.filter(group=self.group).count()
            ),
            (
                another_group_page_data,
                Post.objects.filter(group=self.group2).count()
            ),
            (
                author_page_data,
                Post.objects.filter(author=self.author).count()
            ),
        )
        for data, post_number in tested_data:
            with self.subTest(url=data.tested_url):
                paginator = FakePaginator(post_number)
                self.assertEqual(
                    paginator.records_in_last_page(),
                    data.number_before_add + data.expected_difference
                )

    def test_cash_safe_main_page(self):
        """Проверка хранения и удаления кэша"""
        url = self.url_main_page.url
        post = Post.objects.create(**self.test_post._asdict())
        response = self.authorized_client.get(url)
        posts = response.content
        post.delete()
        response_cached = self.authorized_client.get(url)
        cached_posts = response_cached.content
        cache.clear()
        response_cleared_cache = self.authorized_client.get(url)
        cleared_cache_posts = response_cleared_cache.content
        with self.subTest():
            self.assertEqual(cached_posts, posts)
            self.assertNotEqual(cleared_cache_posts, cached_posts)

    def test_404_get_castom_template(self):
        """Проверка того, что ошибка 404 даёт кастомный шаблон"""
        url = self.url_unnown.url
        template = self.url_unnown.template
        response = self.authorized_client.get(url)
        self.assertTemplateUsed(response, template)

    def test_authorized_client_add_comment(self):
        """Проверка добавления коммента авторизованным пользователем"""
        url = self.url_add_comment.get_url_with_id(
            self.test_comment.post.id
        )
        comments_number_before = Comment.objects.filter(
            post=self.test_comment.post
        ).count()
        response_unauthorised = self.client.post(
            url,
            data=self.test_comment._asdict(),
            follow=True,
        )
        self.authorized_client.post(
            url,
            data=self.test_comment._asdict(),
            follow=True,
        )
        comments_number_after = Comment.objects.filter(
            post=self.test_comment.post
        ).count()
        with self.subTest(url=url):
            self.assertRedirects(
                response_unauthorised,
                self.url_add_comment.get_redirect_to_login(
                    self.test_comment.post.id
                )
            )
            self.assertEqual(
                comments_number_after,
                comments_number_before + 1
            )

    def test_authorized_client_follow_and_unfollow(self):
        """Проверка.
        Авторизованный пользователь может подписываться,
        неавторизованный - нет
        """
        follows_number_base = Follow.objects.filter(
            **self.test_follow._asdict()
        ).count()
        # Follow
        url_followed = self.url_follow.get_url_with_username(
            self.test_follow.author.username
        )

        self.authorized_client.get(url_followed)
        follows_number_authorized = Follow.objects.filter(
            **self.test_follow._asdict()
        ).count()

        # Unfollow
        url_unfollowed = self.url_unfollow.get_url_with_username(
            self.test_follow.author.username
        )
        self.authorized_client.get(url_unfollowed)
        unfollows_number_authorized = Follow.objects.filter(
            **self.test_follow._asdict()
        ).count()

        # Follow unathorized client
        self.client.get(self.url_follow.url)
        follows_number_unauthorized = Follow.objects.filter(
            **self.test_follow._asdict()
        ).count()

        with self.subTest(author=self.test_follow.author.username):
            self.assertEqual(
                follows_number_authorized,
                follows_number_base + 1
            )
            self.assertEqual(
                follows_number_unauthorized,
                follows_number_base
            )
            self.assertEqual(
                unfollows_number_authorized,
                follows_number_base
            )

    def test_post_in_authrized_followers(self):
        """Проверка. Добавленный пост появляется
        только у авторизованных пользователей
        """
        Follow.objects.create(**self.test_follow._asdict())
        url_followed = self.url_follow_list.get_url_with_username(
            self.test_follow.user.username
        )
        url_unfollowed = self.url_follow_list.get_url_with_username(
            self.author3.username
        )

        response = self.authorized_client.get(url_followed)
        count_before_followed = (len(response.context['page_obj']))

        self.authorized_client.force_login(self.author2)

        response = self.authorized_client.get(url_unfollowed)
        count_before_unfollowed = (len(response.context.get('page_obj')))

        self.authorized_client.force_login(self.authorized_user)
        Post.objects.create(
            text=self.fake.text(),
            author=self.test_follow.author,
        )

        response = self.authorized_client.get(url_followed)
        count_after_followed = (len(response.context.get('page_obj')))

        self.authorized_client.force_login(self.author2)

        response = self.authorized_client.get(url_unfollowed)
        count_after_unfollowed = (len(response.context.get('page_obj')))

        with self.subTest(url=url_followed):
            self.assertEqual(
                count_before_followed + 1,
                count_after_followed
            )
            self.assertEqual(
                count_before_unfollowed,
                count_after_unfollowed
            )
