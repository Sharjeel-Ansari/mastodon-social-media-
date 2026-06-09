from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post, Comment


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'post-textarea',
            'placeholder': "What's on your mind?",
            'rows': 3,
        }),
        max_length=500,
    )

    class Meta:
        model = Post
        fields = ('content', 'image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False
        self.fields['image'].widget.attrs.update({'class': 'file-input', 'accept': 'image/*'})


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'comment-input',
            'placeholder': 'Write a comment...',
        }),
        max_length=300,
    )

    class Meta:
        model = Comment
        fields = ('content',)


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'bio', 'website', 'location', 'avatar', 'cover_photo')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ('avatar', 'cover_photo'):
                field.widget.attrs.update({'class': 'form-input'})
            else:
                field.widget.attrs.update({'class': 'file-input'})
                field.required = False
