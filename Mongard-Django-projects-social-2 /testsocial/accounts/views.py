from django.shortcuts import render, redirect
from django.views import View
from .forms import UserRegistrationForm, UserLoginForm, ProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .models import Relation, Profile


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
            messages.success(request, 'Account created...', 'success')
            return redirect('home:home')
        return render(request, self.template_name, {'form': form})


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful.', 'success')
                if self.next:
                    return redirect(self.next)
                return redirect('home:home')
            messages.error(request, 'Login failed.', 'warning')
            return render(request, self.template_name, {'form':form})


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Logout successful.', 'success')
        return redirect('home:home')


class UserProfileView(LoginRequiredMixin, View):

    def get(self, request, user_id):
        is_following = False
        user = User.objects.get(pk=user_id)
        posts = user.posts.all()
        relations = Relation.objects.filter(from_user=request.user, to_user=user)
        if relations.exists():
            is_following = True
        return render(request, 'accounts/profile.html', {'user': user, 'posts': posts, 'is_following': is_following})


class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset.html'
    success_url = reverse_lazy('accounts:user_password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'



class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:user_password_reset_complete')


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'



class UserFollowView(LoginRequiredMixin, View):

    def get(self, request, user_id):
        from_user = User.objects.get(id=request.user.id)
        to_user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(from_user=from_user, to_user=to_user)
        if relation.exists():
            messages.error(request, 'You are already following this user.', 'danger')
        else:
            Relation.objects.create(from_user=from_user, to_user=to_user)
            messages.success(request, 'You are now following this user.', 'success')
        return redirect('accounts:user_profile', to_user.id)


class UserUnfollowView(LoginRequiredMixin, View):

    def get(self, request, user_id):
        from_user = User.objects.get(id=request.user.id)
        to_user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(from_user=from_user, to_user=to_user)
        if relation.exists():
            relation.delete()
            messages.success(request, 'You are not following this user.', 'success')
        else:
            messages.error(request, 'You are not following this user.', 'danger')
        return redirect('accounts:user_profile', to_user.id)


class EditProfileView(LoginRequiredMixin, View):
    form_class = ProfileForm
    template_name = 'accounts/edit_profile.html'

    def get(self, request):
        form = self.form_class(instance=request.user.profile, initial={'email':request.user.email})
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form = self.form_class(request.POST, instance=request.user.profile, initial={'email':request.user.email})
        if form.is_valid():
            form.save()
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'Profile updated.', 'success')
        return redirect('accounts:user_profile', request.user.id)

