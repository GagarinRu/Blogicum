from django.db import models
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.utils import timezone

from blog.constants import CHARFIELD_LENGTH, MAX_DISPLAY_HEADING

User = get_user_model()


class PostCategoryManager(models.Manager):
    def get_queryset(self):
        return PostCategoryQuerySet(self.model, using=self._db)

    def get_comments_count(self):
        return self.get_queryset().get_comments_count()

    def get_active_filter(self):
        return self.get_queryset().get_active_filter()


class PostCategoryQuerySet(models.QuerySet):
    def get_comments_count(self):
        return self.annotate(comment_count=Count('comments'))

    def get_active_filter(self):
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
    objects = PostCategoryManager.from_queryset(PostCategoryQuerySet)()

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
    objects = PostCategoryManager.from_queryset(PostCategoryQuerySet)()

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
        related_name='authors',
        verbose_name='Автор комментария'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:MAX_DISPLAY_HEADING]
