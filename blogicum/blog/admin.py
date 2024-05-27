from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Category, Comment, Location, Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'category',
        'author',
        'location',
    )
    list_display_links = (
        'title',
        'author',
        'location'
    )
    list_editable = (
        'is_published',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('category',)
    empty_value_display = ['empty_image']

    def empty_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="60">')


class PostInline(admin.TabularInline):
    model = Post
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (
        PostInline,
    )
    list_display = ('username', 'posts_count', 'email',
                    'first_name', 'last_name', 'is_staff')

    @admin.display(description='Кол-во постов у пользователя')
    def posts_count(self, obj):
        return obj.posts.count()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'title',
        'is_published',
        'description'
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'name',
        'is_published',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Comment)
class Comment(admin.ModelAdmin):
    list_display = (
        'text',
        'created_at',
    )
    search_fields = ('text',)
    list_filter = ('text',)


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.empty_value_display = 'Не задано'
