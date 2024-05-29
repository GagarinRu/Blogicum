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

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        return self.get_category().posts.publish_filter().annotate_select_comments()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    queryset = Post.objects.annotate_select_comments().publish_filter()
    paginate_by = MAX_DISPLAY_POSTS


class PostDetailView(DetailView):
    model = Post
    form_class = CommentForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = get_object_or_404(
            Post,
            pk=self.kwargs[self.pk_url_kwarg],
        )
        if post.author == self.request.user:
            return post
        return get_object_or_404(
            Post.objects.publish_filter(
            ), pk=self.kwargs[self.pk_url_kwarg]
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
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs[self.pk_url_kwarg]}
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

    def get_profile(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_queryset(self):
        queryset = self.get_profile().posts.annotate_select_comments()
        if self.get_profile() != self.request.user:
            queryset = queryset.publish_filter()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile()
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
