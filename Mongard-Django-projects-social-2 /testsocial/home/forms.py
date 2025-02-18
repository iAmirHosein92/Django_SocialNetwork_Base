from django import forms
from .models import Post, Comment


class PostCreateUpdateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['body', ]


class PostCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body', ]
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your comment...'}),
        }


class ReplyPostCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body', ]
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your reply ...'}),
        }


class PostSearchForm(forms.Form):
    search = forms.CharField()
