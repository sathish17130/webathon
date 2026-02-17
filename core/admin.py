from django.contrib import admin
from .models import Category, SpecificationField, UserItem


class SpecificationFieldInline(admin.TabularInline):
    model = SpecificationField
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = [SpecificationFieldInline]


@admin.register(SpecificationField)
class SpecificationFieldAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "field_type", "weight"]
    list_filter = ["category", "field_type"]
    search_fields = ["name", "category__name"]
    ordering = ["category__name", "name"]


@admin.register(UserItem)
class UserItemAdmin(admin.ModelAdmin):
    list_display = ["item_name", "category", "created_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["item_name", "category__name"]
    readonly_fields = ["created_at"]
