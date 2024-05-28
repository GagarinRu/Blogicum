from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .constants import MAX_DISPLAY_POSTS
from .forms import CommentForm, PostForm, UserProfileForm
from .models import Category, Post, User
from .mixin import OnlyAuthorMixin, PostMixin, CommentMixin


class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category.html'
    paginate_by = MAX_DISPLAY_POSTS

    def get_queryset(self):
        self.category_page = get_object_or_404(
            Category.objects.all(),
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return self.category_page.posts.select_related(
            'author',
            'location',
            'category'
        ).get_active_filter(
        ).get_comments_count(
        ).order_by(
            '-pub_date'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category_page
        return context


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    queryset = Post.objects.get_active_filter(
    ).get_comments_count(
    ).order_by(
        '-pub_date'
    )
    paginate_by = MAX_DISPLAY_POSTS
    ordering = '-pub_date'


class PostDetailView(DetailView):
    model = Post
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def get_object(self):
        post = get_object_or_404(
            Post.objects.all(),
            pk=self.kwargs['post_id'],
        )
        if post.author == self.request.user:
            return post
        else:
            return get_object_or_404(
                Post.objects.get_active_filter(
                ).filter(
                    pk=self.kwargs['post_id'],
                )
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.object
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('post')
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(PostMixin, UpdateView):
    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(PostMixin, DeleteView):
    pass


class CommentCreateView(CommentMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id'],
        )
        return super().form_valid(form)


class CommentUpdateView(CommentMixin, OnlyAuthorMixin, UpdateView):
    pass


class CommentDeleteView(CommentMixin, OnlyAuthorMixin, DeleteView):
    pass


class ProfileDetailView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = MAX_DISPLAY_POSTS

    def get_queryset(self):
        username = self.kwargs['username']
        profile = get_object_or_404(User, username=username)
        queryset = profile.posts.select_related(
            'location',
            'author',
            'category'
        ).filter(
            author=profile
        ).get_comments_count(
        ).order_by(
            '-pub_date'
        )
        if profile != self.request.user:
            return queryset.get_active_filter()
        else:
            return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        context['profile'] = profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.object.username}
        )


class RegistrationCreate(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')
