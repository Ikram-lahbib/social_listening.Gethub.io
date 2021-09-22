from django.conf.urls import url
from django.urls import path

#from . views import All_posts, Post
from . import views

app_name = 'Search'


urlpatterns = [
	url(r'^$', views.All_posts, name='All_posts'),
	url(r'^(?P<id>\d+)$', views.Post, name='Post'),

	url('register/', views.registerPage, name="register"),
	path('login/', views.loginPage, name="login"),
	path('logout/', views.logoutUser, name="logout"),
	path('<id>-<src>/analyse_sentiment/', views.Analyse_sentiment, name="Analyse_sentiment"),
	#url(r'^(?P<id>\d+)/analyse_sentiment$', views.Analyse_sentiment, name="Analyse_sentiment"),
	url(r'^(?P<id>\d+)/delete$', views.Delete_post, name='Delete_post'),

	url(r'^create$', views.Create_post, name='Create_post'),
	url(r'^(?P<id>\d+)/edit$', views.Edit_post, name='Edit_post'),
	url(r'^(?P<id>\d+)/scraping$', views.Scraping, name='Scraping'),
	url(r'^(?P<id>\d+)/importing$',views.Importing_data, name='Importing_data'),
	url(r'^template$',views.template, name='template'),
]
