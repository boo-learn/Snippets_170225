from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.contrib import messages

from MainApp.forms import SnippetForm, CommentForm
from MainApp.models import Snippet, Comment


class AddSnippetView(LoginRequiredMixin, CreateView):
    """Создание нового сниппета"""
    model = Snippet
    form_class = SnippetForm
    template_name = 'pages/add_snippet.html'
    success_url = reverse_lazy('snippets-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'Создание сниппета'
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Success!!!")
        return super().form_valid(form)


class SnippetDetailView(DetailView):
    model = Snippet
    template_name = 'pages/snippet_detail.html'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        snippet = Snippet.objects.prefetch_related(
            Prefetch('comments',
                     queryset=Comment.with_likes_count().select_related('author')),
            "tags")
        return snippet

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments_form = CommentForm()
        snippet = self.get_object()
        context['pagename'] = f'Сниппет: {snippet.name}'
        context["comments_form"] = comments_form
        return context