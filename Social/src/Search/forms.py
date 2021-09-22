from django import forms
from .models import Search

# for regester and loginPage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# ++++++++++++++++++++++++++

class PostForm(forms.ModelForm):
	class Meta:
		model = Search
		fields = ['project_name']

class import_dataForm(forms.Form):
    text_search= forms.CharField(max_length=100)


# for regester and loginPage
class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']
