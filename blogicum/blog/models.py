from django.db import models
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.utils import timezone

from blog.constants import CHARFIELD_LENGTH, MAX_DISPLAY_HEADING

User = get_user_model()


class PostQuerySet(models.QuerySet):
    def annotate_select_comments(self):
        return self.select_related(
            'author',
            'location',
            'category'
        ).annotate(
            comment_count=Count('comments')
        ).order_by(
            '-pub_date'
        )

    def publish_filter(self):
        return self.filter(
            pub_date__date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )


class CreatedAt(models.Model):
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        ordering = ('created_at',)
        abstract = True


class IsPublishedCreatedAt(CreatedAt):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True


class Location(IsPublishedCreatedAt):
    name = models.CharField(
        'Название места',
        max_length=CHARFIELD_LENGTH
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:MAX_DISPLAY_HEADING]


class Category(IsPublishedCreatedAt):
    title = models.CharField(
        'Заголовок',
        max_length=CHARFIELD_LENGTH
    )
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:MAX_DISPLAY_HEADING]


class Post(IsPublishedCreatedAt):
    title = models.CharField(
        'Заголовок',
        max_length=CHARFIELD_LENGTH
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
        'можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='post_images',
        blank=True
    )
    objects = PostQuerySet.as_manager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'

    def __str__(self):
        return self.title[:MAX_DISPLAY_HEADING]


class Comment(CreatedAt):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Заголовок поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )

    class Meta(CreatedAt.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:MAX_DISPLAY_HEADING]
