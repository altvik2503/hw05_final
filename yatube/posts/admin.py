from django.contrib import admin
from .models import Group, Post

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


admin.site.register(Group)
admin.site.register(Post, PostAdmin)
