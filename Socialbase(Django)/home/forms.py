from django import forms
from .models import Post, Like, Comment


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Content'}),
        }


class UpdatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Content'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body', )
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write Your Comment...'}),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body', )
        widgets = {
            'body':forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write Your Reply...'}),
        }


class SearchForm(forms.Form):
    search = forms.CharField(label='Search', max_length=100)