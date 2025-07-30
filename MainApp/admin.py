from django.contrib import admin
from .models import Snippet, Tag
from django.db.models import Count


class SnippetAdmin(admin.ModelAdmin):
    list_display = ("name", "lang", "public", "num_comments")
    list_filter = ("lang", "public")

    # Метод для получения queryset с аннотированным полем
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Аннотируем каждую запись количеством комментариев
        queryset = queryset.annotate(
            num_comments=Count('comments', distinct=True)
        )
        return queryset

    # Добавление пользовательского поля
    def num_comments(self, obj):
        return obj.num_comments

    # Определение заголовка для пользовательского поля
    num_comments.short_description = 'Кол-во комментариев'

class TagAdmin(admin.ModelAdmin):
    list_display = ("name", )


# Register your models here.
admin.site.register(Snippet, SnippetAdmin)
admin.site.register(Tag, TagAdmin)
