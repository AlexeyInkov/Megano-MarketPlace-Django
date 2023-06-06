from django.contrib import admin

from .models import (
    Image,
    Profile,
    Category,
    Tag,
    Review,
    Specification,
    Sale,
    Product
)


# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = 'id', 'user', 'phone', 'avatar'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'id', 'title', 'image', 'parent'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = 'id', 'title', 'category', 'price', 'count', 'freeDelivery'


admin.site.register(Tag, admin.ModelAdmin)
admin.site.register(Image, admin.ModelAdmin)
admin.site.register(Review, admin.ModelAdmin)
admin.site.register(Specification, admin.ModelAdmin)

