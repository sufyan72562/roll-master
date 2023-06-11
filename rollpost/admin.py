from django.contrib import admin
from rollpost.models import Posts,Comment,CommentReply,ThreadPost,ReportAdmin

# Register your models here.
admin.site.register((CommentReply,Comment,ThreadPost,ReportAdmin))

@admin.register(Posts)
class DatasetAdmin(admin.ModelAdmin):
    list_display= ("id","user")
