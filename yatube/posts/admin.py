from django.contrib import admin
from .models import Group, Post, Comment

DEFAULT_FIELD_VALUE = '-пусто-'


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group', )
    search_fields = ('text', )
    list_filter = ('pub_date', )
    empty_value_display = DEFAULT_FIELD_VALUE


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'post',
        'author',
        'created',
    )
    list_filter = ('author', 'created', )
    search_fields = ('text', )


admin.site.register(Comment, CommentAdmin)
admin.site.register(Group)
admin.site.register(Post, PostAdmin)
