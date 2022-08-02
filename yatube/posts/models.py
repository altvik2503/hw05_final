from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Группа',
        max_length=200,
        blank=False,
        null=False,
        help_text='Группа, к которой будет относиться пост',
    )
    slug = models.SlugField(
        unique=True,
        blank=False,
        null=False,
    )
    description = models.TextField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)


class Post(models.Model):
    RELATED_NAME = 'posts'
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста',
        blank=False,
        null=False,
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name=RELATED_NAME,
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name=RELATED_NAME,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    RELATED_NAME = 'comments'
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name=RELATED_NAME,
        verbose_name='Пост',
        help_text='Комментируемый пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name=RELATED_NAME,
        verbose_name='Автор комментария',
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Текст нового комментария',
        blank=False,
        null=False,
    )
    created = models.DateTimeField(
        'Дата комментария',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        blank=False,
        null=False,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        blank=False,
        null=False,
    )
