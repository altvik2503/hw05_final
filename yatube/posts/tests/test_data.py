# posts/tests/test_data.py
from collections import namedtuple
from dataclasses import dataclass
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from faker import Faker
from http import HTTPStatus
import math
import shutil
import tempfile

from posts.models import Post, Group

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

TestComment = namedtuple('TestComment', ('text',  'author', 'post'))
TestFollow = namedtuple('TestFollow', ('author', 'user'))
TestPost = namedtuple('TestPost', ('text', 'group', 'author', 'image'))
TestGroup = namedtuple('TestGroup', ('title', 'slug', 'description'))
PostFormData = namedtuple('PostFormData', ('text', 'group', 'image'))
PostFormFieldsTypes = namedtuple(
    'PostFormFieldsTypes',
    ('text', 'group', 'image')
)


@dataclass
class FakePaginator():
    records_number: int
    records_per_page: int = 10

    def pages(self):
        return math.ceil(self.records_number / self.records_per_page)

    def records_in_last_page(self):
        number = self.records_number % self.records_per_page
        if not number:
            number = self.records_per_page
        return number


@dataclass
class UrlViewData():
    url: str
    name: str = None
    template: str = None
    redirect: str = None
    accessed_authorised_client: bool = False
    status: HTTPStatus = HTTPStatus.OK
    kwargs: str = None

    def _get_attr_with_mask(self, field, mask, value=None):
        attr = None
        if hasattr(self, field):
            attr = getattr(self, field)
        if id is None or attr is None:
            return attr
        return attr.replace(mask, str(value))

    def get_url_with_id(self, id=None):
        return self._get_attr_with_mask('url', '<id>', id)

    def get_url_with_username(self, username=None):
        return self._get_attr_with_mask('url', '<username>', username)

    def get_redirect_with_id(self, id=None):
        return self._get_attr_with_mask('redirect', '<id>', id)

    def get_url_from_name(self, id=None):
        kwards = self.kwargs
        if id is None or kwards is None:
            return reverse(self.name)
        kwards = kwards.replace('<id>', str(id))
        kwards = kwards.replace(' ', '')
        kwards = kwards.split(':')
        return reverse(self.name, kwargs=dict([kwards]))

    def get_last_page_url(self, page_num):
        return ''.join((self.url, '?page=', str(page_num)))


class DataTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.fake = Faker()
        
        # Create base urls
        cls.url_main_page = UrlViewData(
            url='/',
            name='posts:index',
            template='posts/index.html',
        )
        cls.url_group = UrlViewData(
            url='/group/test_slug/',
            name='posts:group_list',
            template='posts/group_list.html',
            kwargs='slug: test_slug'
        )
        cls.url_group2 = UrlViewData(
                url='/group/slug2/',
                name='posts:group_list',
                template='posts/group_list.html',
                kwargs='slug: slug2'
        )
        cls.url_auth = UrlViewData(
            url='/profile/auth/',
            name='posts:profile',
            template='posts/profile.html',
            kwargs='username: auth'
        )
        cls.url_detail = UrlViewData(
            url='/posts/<id>/',
            name='posts:post_detail',
            template='posts/post_detail.html',
            kwargs='post_id: <id>',
        )
        cls.url_create = UrlViewData(
            url='/create/',
            name='posts:post_create',
            template='posts/create_post.html',
            redirect='/',
            accessed_authorised_client=True,
        )
        cls.url_edit = UrlViewData(
            url='/posts/<id>/edit/',
            name='posts:post_edit',
            template='posts/create_post.html',
            redirect='/posts/<id>/',
            accessed_authorised_client=True,
            kwargs='post_id: <id>'
        )
        cls.url_unnown = UrlViewData(
            url='/unexpected_page/',
            template='core/404.html',
            status=HTTPStatus.NOT_FOUND,
        )
        cls.url_add_comment = UrlViewData(
            url='/posts/<id>/comment/',
            template='posts/includes/add_comment.html',
            redirect='/posts/<id>/',
            accessed_authorised_client=True,
            kwargs='post_id: <id>'
        )
        cls.url_follow_list = UrlViewData(
            url='/follow/',
            name='posts:follow_index',
            template='posts/follow.html',
            accessed_authorised_client=True,
        )
        cls.url_follow = UrlViewData(
            url='/profile/<username>/follow/',
            name='posts:profile_follow',
            accessed_authorised_client=True,
        )
        cls.url_unfollow = UrlViewData(
            url='/profile/<username>/unfollow/',
            name='posts:profile_unfollow',
            accessed_authorised_client=True,
        )

        # Create users
        cls.author = User.objects.create_user(username='auth')
        cls.author2 = User.objects.create_user(username='auth2')
        cls.author3 = User.objects.create_user(username='auth3')
        cls.authorized_user = User.objects.get(username='auth')

        # Create test_groups
        cls.test_group = TestGroup(
            title = cls.fake.text(),
            slug = 'test_slug',
            description = cls.fake.text(),
        )
        cls.test_group2 = TestGroup(
            title = cls.fake.text(),
            slug = 'slug2',
            description = cls.fake.text(),
        )
        cls.group = Group.objects.create(**cls.test_group._asdict())
        cls.group2 = Group.objects.create(**cls.test_group2._asdict())

        # Create test image
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        small_gif2 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x00'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.image2 = SimpleUploadedFile(
            name='small2.gif',
            content=small_gif2,
            content_type='image/gif'
        )

        # Create test_posts
        cls.test_post = TestPost(
            text=cls.fake.text(),
            author=cls.author,
            group=cls.group,
            image=cls.image,
        )
        cls.post = Post.objects.create(**cls.test_post._asdict())
        
        # Create test comment
        cls.test_comment = TestComment(
            text=cls.fake.text(),
            post=cls.post,
            author=cls.author2,
        )

        # Create test follow
        cls.test_follow = TestFollow(
            author=cls.author3,
            user=cls.author
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.authorized_user)
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
