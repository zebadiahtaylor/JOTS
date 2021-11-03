from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Collection, Note, Tag, Article

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email',)
    ordering = ('username',)

class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'leader', 'active', 'is_public')

class NoteAdmin(admin.ModelAdmin):
    list_display = ('collection', 'created_at', 'updated_at', 'updated_by')

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'collection')

class ArticleAdmin(admin.ModelAdmin):
    list_dsplay = ('title', 'collection', 'created_by', 'updated_by', 'views')


admin.site.register(User, UserAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Article, ArticleAdmin)