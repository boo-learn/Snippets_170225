from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Q
from MainApp.models import Snippet
from MainApp.forms import SnippetForm, UserRegistrationForm
from MainApp.models import LANG_ICON
from django.contrib import auth
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm


def get_icon(lang):
    return LANG_ICON.get(lang)


def index_page(request):
    context = {'pagename': 'PythonBin'}
    return render(request, 'pages/index.html', context)


@login_required
def add_snippet_page(request):
    if request.method == 'GET':
        form = SnippetForm()
        context = {'form': form, "pagename": "Создание сниппета"}
        return render(request, 'pages/add_snippet.html', context)

    if request.method == 'POST':
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.user = request.user
            snippet.save()
            return redirect('snippets-list')
        else:
            context = {'form': form, "pagename": "Создание сниппета"}
            return render(request, 'pages/add_snippet.html', context)


def snippets_page(request):
    if not request.user.is_authenticated: # not auth: all public snippets
        snippets = Snippet.objects.filter(public=True)
    else: # auth:     all public snippets + OR self private snippets
        snippets = Snippet.objects.filter(Q(public=True) | Q(public=False, user=request.user))


    for snippet in snippets:
        snippet.icon = get_icon(snippet.lang)
    context = {
        'pagename': 'Просмотр сниппетов',
        'snippets': snippets,
    }
    return render(request, 'pages/view_snippets.html', context)


@login_required
def snippets_my(request):
    snippets = Snippet.objects.filter(user=request.user)
    context = {
        'pagename': 'Мои сниппетов',
        'snippets': snippets,
    }
    return render(request, 'pages/view_snippets.html', context)


def snippet_detail(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    snippet.views_count = F('views_count') + 1
    snippet.save(update_fields=['views_count'])
    snippet.refresh_from_db()
    context = {
        "snippet": snippet
    }
    return render(request, 'pages/snippet_detail.html', context)


def snippet_delete(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    snippet.delete()
    return redirect('snippets-list')


def snippet_edit(request, id):
    if request.method == "GET":
        snippet = get_object_or_404(Snippet, id=id)
        form = SnippetForm(instance=snippet)
        context = {
            "pagename": "Редактировать Сниппет",
            "form": form,
            "edit": True,
            "id": id
        }
        return render(request, 'pages/add_snippet.html', context)

    if request.method == "POST":
        snippet = get_object_or_404(Snippet, id=id)
        form = SnippetForm(request.POST, instance=snippet)
        if form.is_valid():
            form.save()

        return redirect('snippets-list')


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            context = {
                "errors": ["Некорректные данные"],

            }
            return render(request, "pages/index.html", context)


def user_logout(request):
    auth.logout(request)
    return redirect('home')


def user_registration(request):
    if request.method == "GET":
        user_form = UserRegistrationForm()
        context = {
            "user_form": user_form
        }
        return render(request, "pages/registration.html", context)

    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            return redirect("home")
        else:
            context = {
                "user_form": user_form
            }
            return render(request, "pages/registration.html", context)