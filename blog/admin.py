from django.contrib import admin
from blog import models
# Register your models here.

# @admin.register(UserInfo)
# class UserInfoAdmin(admin.ModelAdmin):
#     list_display = ['username', 'avatar', 'telephone']
admin.site.register(models.UserInfo)
admin.site.register(models.Article)
admin.site.register(models.ArticleUpDown)
admin.site.register(models.Blog)
admin.site.register(models.Comment)
admin.site.register(models.Category)
admin.site.register(models.Tag)