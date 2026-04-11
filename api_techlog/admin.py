# api_techlog/admin.py
from django.contrib import admin
from .models import Category, Tag, Post, Like, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['id', 'name', 'created_at']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display  = ['id', 'name', 'created_at']
    search_fields = ['name']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display   = ['title', 'author', 'category', 'status', 'views', 'created_at']
    list_filter    = ['status', 'category']
    search_fields  = ['title', 'content']
    filter_horizontal = ['tags']   # ManyToManyを選択しやすくする
    readonly_fields   = ['views', 'created_at', 'updated_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ['author', 'post', 'content', 'created_at']
    search_fields = ['content']
    readonly_fields = ['created_at', 'updated_at']
