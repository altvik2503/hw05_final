from dataclasses import dataclass
from django.urls import reverse
from http import HTTPStatus


@dataclass
class UrlViewData():
    """ Возможные варианты
    Просто адрес - '/'
    Имя - 'posts:index'
    Шаблон - 'posts/index.html'

    Возможные редиректы
    на страницу авторизации - '/auth/login/'
    на статическую страницу - '/posts/index/
    на динамичекскую стрраеицу - '/posts/<id>/'

    Возможные атрибуты
    id - '/posts/<id>/', '/posts/<id>/edit/'
    slug - '/group/<slug>/'
    username - '/<username>/
    page - '/posts/?page=<page>'
    login - '/auth/login/?next=<source_url>/


    """
    url: str
    name: str = None
    template: str = None
    redirect: str = None
    accessed_authorised_client: bool = False
    kwargs: str = None
    status: HTTPStatus = HTTPStatus.OK
    login_url = reverse('users:login')

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

    def get_redirect_to_login(self, id=None):
        return f'{self.login_url}?next={self.get_url_with_id(id)}'

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
