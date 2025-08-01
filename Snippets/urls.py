from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from MainApp import views
from django.contrib import admin

urlpatterns = [
    path('', views.index_page, name="home"),
    path('snippets/add', views.add_snippet_page, name="snippet-add"),
    path('snippets/list', views.snippets_page, {'snippets_my': False}, name="snippets-list"),
    path('snippets/my', views.snippets_page, {'snippets_my': True}, name="snippets-my"),
    path('snippet/<int:id>', views.snippet_detail, name="snippet-detail"),
    path('snippet/<int:id>/delete', views.snippet_delete, name="snippet-delete"),
    path('snippet/<int:id>/edit', views.snippet_edit, name="snippet-edit"),
    path('login', views.login, name="login"),
    path('logout/', views.user_logout, name='logout'),
    path('registration/', views.user_registration, name='registration'),
    path('comment/add', views.comment_add, name="comment_add"),
    path('admin/', admin.site.urls),
]

# snippets/list
# snippets/list?sort=name
# snippets/list?sort=lang
# snippets/list?sort=create_date
