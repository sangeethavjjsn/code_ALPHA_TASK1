from django import forms
from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post, Comment
from django.contrib.auth.forms import AuthenticationForm

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'bio', 'profile_pic', 'password1', 'password2']
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption', 'image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'bio']
        widgets = {
            'profile_pic': forms.FileInput(attrs={'class': 'form-control d-none', 'id': 'id_profile_pic'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }