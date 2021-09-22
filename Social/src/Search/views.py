import json
import os.path
from os import path
from pymongo import MongoClient
from time import sleep

from django.shortcuts import render, get_object_or_404, redirect
# Create your views here.
from . models import Search
from . forms import PostForm, import_dataForm, CreateUserForm
from django.contrib import messages
from . Scraping import Scraping_youtube , Methods, Scraping_twitter
from . Analyse_sentiment import Sentiment
# *****************************************************************************
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .decorators import unauthenticated_user, allowed_users, admin_only



@unauthenticated_user
def registerPage(request):
	if request.user.is_authenticated:
		return redirect('Search:All_posts')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				user = form.cleaned_data.get('username')
				messages.success(request, 'Account was created for ' + user)

				return redirect('Search:login')

		context = {'form':form}
		return render(request, 'register.html', context)

@unauthenticated_user
def loginPage(request):
	if request.user.is_authenticated:
		return redirect('Search:All_posts')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password =request.POST.get('password')

			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('Search:All_posts')
			else:
				messages.info(request, 'Username OR password is incorrect')

		context = {}
		return render(request, 'login.html', context)

def logoutUser(request):
	logout(request)
	return redirect('Search:login')

# *****************************************************************************
@login_required(login_url='Search:login')
def All_posts(request):
	l = []
	All_posts = Search.objects.all()

	for post in All_posts:
		if post.user == request.user:
			l.append(post)
		else:
			pass

	context = {
		'All_posts' : l,
	}

	return render(request, 'All_posts.html', context)

@login_required(login_url='Search:login')
def Post(request, id):

	#post = Search.objects.get(id=id)
	Post = get_object_or_404(Search, id=id)

	circle = './static/analyse/img/'+str(request.user)+"_"+str(id)+'_circle.png'
	plot1 = '/static/analyse/img/'+str(request.user)+"_"+str(id)+'_plot1.png'
	plot2 = '/static/analyse/img/'+str(request.user)+"_"+str(id)+'_plot2.png'
	plot3 = '/static/analyse/img/'+str(request.user)+"_"+str(id)+'_plot3.png'

	tableaus = '/static/analyse/img/les_tableaus1.png'

	if not os.path.exists(circle):
		tableaus = '/static/analyse/img/les_tableaus.png'

	context = {
		'Post' : Post,
		'circle' : circle,
		'plot1'   : plot1,
		'plot2'   : plot2,
		'plot3'   : plot3,
		'tableau' : tableaus
	}

	return render(request, 'detail.html', context)

@login_required(login_url='Search:login')
def Create_post(request):

	if request.method == 'POST':
		form = PostForm(request.POST)
		if form.is_valid(): # if this information complit

			new_form = form.save(commit=False) # save but not in db (False)
			new_form.user = request.user # add user from request responcible for this request
			new_form.save() # save the all request with user request
			messages.success(request, 'Project created successfully')
			return redirect('/') # reurn to home page

	else:
		form = PostForm()

	context = {
		'form' : form
	}

	return render(request, 'Create.html', context)


@login_required(login_url='Search:login')
def Edit_post(request, id):

	post = get_object_or_404(Search, id=id)

	if request.method == 'POST':
		form = PostForm(request.POST, instance=post)
		if form.is_valid(): # if this information complit

			new_form = form.save(commit=False) # save but not in db (False)
			new_form.user = request.user # add user from request responcible for this request
			new_form.save() # save the all request with user request
			return redirect('/') # reurn to home page

	else:
		form = PostForm(instance=post)

	context = {
		'form' : form
	}

	return render(request, 'Edit.html', context)


@login_required(login_url='Search:login')
def Delete_post(request, id):

	post = get_object_or_404(Search, id=id)

	post.delete()
	Methods.delete_data_in_mongoDB(request.user, id) # delete data scraping in mongoDb
	return redirect('/') # reurn to home page



@login_required(login_url='Search:login')
def Scraping(request , id):

	post = get_object_or_404(Search, id=id)
	if request.method == 'POST':
		form = import_dataForm(request.POST or None)
		if form.is_valid(): # if this information complit

			text_search = form.cleaned_data.get("text_search")
			date1_search = request.POST.get("date1")
			date2_search = request.POST.get("date2")

			youtube = request.POST.get("youtube")
			twitter = request.POST.get("twitter")

			if youtube != None:
				Scraping_youtube.Scraping(text_search, date1_search, date2_search)
				Methods.save_data_in_mongoDB(request.user, id) # save data scraping in mongoDb
				return redirect('Search:Analyse_sentiment', id=id, src='youtube') # reurn to home page
			if twitter != None:

				Scraping_twitter.Scraping(text_search, request.user, id, date1_search, date2_search)
				return redirect('Search:Analyse_sentiment', id=id, src='twitter') # reurn to home page
	else:
		form = import_dataForm()

	context = {
		'form' : form
	}

	return render(request, 'Scraping.html', context)


@login_required(login_url='Search:login')
def Importing_data(request, id):

	return redirect('Search:Post', id=id) # reurn to home page

@login_required(login_url='Search:login')
def Analyse_sentiment(request, src, id=id):


	# training data geted from mongoDB
	Sentiment.train(request.user, id, src)
	df = Sentiment.mongo_get_data_clean(request.user, id, src)
	# get the figure of our df
	Sentiment.circle(df, request.user, id)
	Sentiment.plot1(df, request.user, id)
	Sentiment.plot2(df, request.user, id)
	Sentiment.plot3(df, request.user, id)


	return redirect('Search:Post', id=id)

@login_required(login_url='Search:login')
def template(request):

	f = 'Methods'
	context = {
		'content' : f
	}

	return render(request, 'my_interface.html', context)

# ######################## prt logique #################################
