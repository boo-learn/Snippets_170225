import logging
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Q
from MainApp.models import Snippet, Comment, LANG_CHOICES
from MainApp.forms import SnippetForm, UserRegistrationForm, CommentForm
from MainApp.models import LANG_ICON
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib import messages
from MainApp.signals import snippet_view

# from django.contrib.auth.forms import UserCreationForm
logger = logging.getLogger(__name__)

# error -> danger
# debug -> dark
def index_page(request):
    context = {'pagename': 'PythonBin'}
    # messages.success(request, "1. Успешное!")
    # messages.info(request, "2. Информационное!")
    # messages.warning(request, "3. Предупреждение!")
    # messages.error(request, "4. Ошибка!")
    # messages.debug(request, "5. Отладка!")
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
            messages.error(request, f"Форма заполнена неверно")
            return render(request, 'pages/add_snippet.html', context)


# snippets/list
# snippets/list?sort=name
# snippets/list?sort=lang
# 1. Нет сортировки
# 2. сортировка A-Z
# 3. сортировка Z-A

# snippets/list?page=3

# /snippets/my?lang=python&user_id=1

# /snippets/list?tag=basic

def snippets_page(request, snippets_my):
    if snippets_my:  # url: snippets/my
        if not request.user.is_authenticated:
            return HttpResponse('Unauthorized', status=401)
        snippets = Snippet.objects.filter(user=request.user)
    else:
        if not request.user.is_authenticated:  # not auth: all public snippets
            snippets = Snippet.objects.filter(public=True)
        else:  # auth:     all public snippets + OR self private snippets
            snippets = Snippet.objects.filter(Q(public=True) | Q(public=False, user=request.user))

    # filter
    lang = request.GET.get("lang")
    if lang:
        snippets = snippets.filter(lang=lang)
    user_id = request.GET.get("user_id")
    if user_id:
        snippets = snippets.filter(user__id=user_id)

    # sort
    sort = request.GET.get("sort")
    if sort:
        snippets = snippets.order_by(sort)

    # tag
    tag = request.GET.get("tag")
    if tag:
        snippets = snippets.filter(tags__name=tag)
    # pagination
    paginator = Paginator(snippets, 5)
    num_page = request.GET.get("page")
    page_obj = paginator.get_page(num_page)

    context = {
        'pagename': 'Просмотр сниппетов',
        'page_obj': page_obj,
        'sort': sort,
        'lang': lang,
        'LANG_CHOICES': LANG_CHOICES,
        'users': User.objects.all()
    }
    return render(request, 'pages/view_snippets.html', context)


def snippet_detail(request, id):
    # snippet = get_object_or_404(Snippet, id=id)
    snippet = Snippet.objects.prefetch_related("comments").get(id=id)
    snippet_view.send(sender=None, snippet=snippet)
    comments_form = CommentForm()
    # comments = Comment.objects.filter(snippet=snippet)
    comments = snippet.comments.all()
    context = {
        "snippet": snippet,
        "comments_form": comments_form,
        "comments": comments
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
        logger.debug("Это отладочное сообщение.")
        logger.info("Пользователь посетил страницу.")
        logger.warning("Возможно, что-то пошло не так.")
        logger.error("Произошла ошибка!")
        logger.critical("Приложение в критическом состоянии!")

        user_form = UserRegistrationForm()
        context = {
            "user_form": user_form
        }
        return render(request, "pages/registration.html", context)

    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            messages.success(request, f"Пользователь {user.username} успешно зарегистрирован")
            return redirect("home")
        else:
            context = {
                "user_form": user_form
            }
            return render(request, "pages/registration.html", context)


def comment_add(request):
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        snippet_id = request.POST.get('snippet_id')  # Получаем ID сниппета из формы
        snippet = get_object_or_404(Snippet, id=snippet_id)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user  # Текущий авторизованный пользователь
            comment.snippet = snippet
            comment.save()

        return redirect('snippet-detail',
                        id=snippet_id)  # Предполагаем, что у вас есть URL для деталей сниппета с параметром pk

    raise Http404
