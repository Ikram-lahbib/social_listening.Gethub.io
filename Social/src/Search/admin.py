from django.contrib import admin

# Register your models here.

from .models import Search

class PostAdmin(admin.ModelAdmin):
	list_filter = ['created']
	list_display= ['project_name','created']
	search_field= ['project_name']

admin.site.register(Search, PostAdmin)