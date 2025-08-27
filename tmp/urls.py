from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from MainApp import views, views_cbv
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
    path('', views.index_page, name="home"),
    # path('snippets/add', views.add_snippet_page, name="snippet-add"),
    path('snippets/add', views_cbv.AddSnippetView.as_view(), name="snippet-add"),
    # path('snippets/list', views.snippets_page, {'my_snippets': False}, name="snippets-list"),
    path('snippets/list', views_cbv.SnippetsListView.as_view(), {'my_snippets': False}, name="snippets-list"),
    # path('snippets/my', views.snippets_page, {'my_snippets': True}, name="snippets-my"),
    path('snippets/my', views_cbv.SnippetsListView.as_view(), {'my_snippets': True}, name="snippets-my"),
    # path('snippet/<int:id>', views.snippet_detail, name="snippet-detail"),
    path('snippet/<int:id>', views_cbv.SnippetDetailView.as_view(), name="snippet-detail"),
    # path('snippet/<int:id>/edit', views.snippet_edit, name="snippet-edit"),
    path('snippet/<int:id>/edit', views_cbv.SnippetEditView.as_view(), name="snippet-edit"),
    path('snippet/<int:id>/delete', views.snippet_delete, name="snippet-delete"),

    path('login', views.login, name="login"),
    # path('logout', views.user_logout, name='logout'),
    path('logout', views_cbv.LogoutView.as_view(), name='logout'),
    # path('registration', views.user_registration, name='registration'),
    path('registration', views_cbv.UserRegistrationView.as_view(), name='registration'),
    path('comment/add', views.comment_add, name="comment_add"),
    path('notifications/', views.user_notifications, name="notifications"),
    path('profile/', views.user_profile, name="profile"),
    path('profile/edit/', views.edit_profile, name="edit-profile"),
    path('password/change/', views.password_change, name="password_change"),
    path('activate/<int:user_id>/<str:token>/', views.activate_account, name="activate-account"),
    path('resend_email/', views.resend_email, name="resend-email"),

    path('api/notifications/unread-count', views.unread_notifications_count, name="unread_notifications_count"),
    path('api/is_authenticated', views.is_authenticated, name="unread_notifications_count"),
    path('api/comment/like', views.add_commen_like, name="unread_notifications_count"),
    # path('comment/<int:id>/liked', views.comment_like, {'vote': 1}, name="comment-like"),
    # path('comment/<int:id>/disliked', views.comment_like, {'vote': -1}, name="comment-dislike"),
]

# Добавляем debug_toolbar URLs только в режиме разработки
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass

# Добавляем обработку статических файлов только в режиме разработки
# В продакшене Django использует встроенную обработку статических файлов
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# /notification/5/delete
# /notifications/read/delete

# /comment/3/like
# /comment/2/dislike
