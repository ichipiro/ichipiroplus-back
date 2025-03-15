from django.contrib import admin

from articles.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
