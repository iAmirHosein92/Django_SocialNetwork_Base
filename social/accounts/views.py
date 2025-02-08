from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from home.models import Post
from  django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(username=cd['username'], email=cd['email'], password=cd['password1'])
            messages.success(request, 'Account created successfully', 'success')
            return redirect('home:home')
        return render(request, self.template_name, {'form': form})



class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'Account logged in', 'success')
                return redirect('home:home')
            messages.error(request, 'Invalid username or password', 'warning')
            return render(request, self.template_name, {'form': form})


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Successfully logged out', 'success')
        return redirect('home:home')


class UserProfileView(LoginRequiredMixin, View):

    def get(self, request, user_id):
        user = get_object_or_404(Post, pk=user_id)
        posts = Post.objects.filter(user=user)
        return render(request, 'accounts/profile.html', {'user': user, 'posts':posts})


class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    success_url = reverse_lazy('accounts:user_reset_password_done')
    email_template_name = 'accounts/password_reset_email.html'


class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:user_reset_password_complete')


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'