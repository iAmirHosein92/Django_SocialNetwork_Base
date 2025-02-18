from django.shortcuts import render, redirect, get_object_or_404
from home.models import Post
from django.contrib import messages
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm, UserLoginForm, EditProfileForm
from .models import Relation, Profile
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

class UserLogoutView(LoginRequiredMixin, View):

    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out.', 'success')
        return redirect('home:home')

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
            User.objects.create_user(
                username=cd['username'],
                email=cd['email'],
                password=cd['password'],
            )
            messages.success(request, 'Account created.', 'success')
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
            messages.success(request, 'You have been logged in.', 'success')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form  = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'Logged In Successfully.', 'success')
                if self.next:
                    return redirect(self.next)
                return redirect('home:home')
            messages.error(request, 'Invalid username or password.', 'danger')
        return render(request, self.template_name, {'form': form})


class UserProfileView(LoginRequiredMixin, View):
    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You are not authenticated.You Should Login First...', 'danger')
            return redirect('accounts:user_login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        post_instance = Post.objects.filter(author=kwargs['user_id'])
        relations = Relation.objects.filter(from_user=request.user, to_user=kwargs['user_id'])
        is_following = False
        user = get_object_or_404(User, id=kwargs['user_id'])
        posts = post_instance
        if relations.exists():
            is_following = True
        if self.next:
            return redirect(self.next)

        return render(request, 'accounts/profile.html', {'user': user, 'posts': posts, 'is_following': is_following})


class UserFollowView(LoginRequiredMixin, View):

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You are not authenticated', 'danger')
            return redirect('accounts:user_login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['user_id'])
        if self.next:
            return redirect(self.next)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            messages.error(request, 'You are already following', 'danger')
        else:
            Relation.objects.create(from_user=request.user, to_user=user)
            messages.success(request, 'You are now following ' + user.username, 'success')
        return redirect('accounts:user_profile' ,user.id)


class UserUnfollowView(LoginRequiredMixin, View):

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You are not authenticated', 'danger')
            return redirect('accounts:user_login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['user_id'])
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if self.next:
            return redirect(self.next)
        if relation.exists():
            relation.delete()
            messages.success(request, 'You are no longer following ' + user.username, 'success')
        else:
            messages.error(request, 'You are not following ' + user.username, 'danger')
        return redirect('accounts:user_profile' ,user.id)


class EditProfileView(LoginRequiredMixin, View):
    form_class = EditProfileForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You are not authenticated', 'danger')
            return redirect('accounts:user_login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form =self.form_class(instance=request.user.profile, initial={'email': request.user.email})
        return render(request, 'accounts/edit_profile.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'Profile updated.', 'success')
        return redirect('accounts:user_profile', request.user.id)


class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    success_url = reverse_lazy('accounts:user_password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'


class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:user_password_reset_complete')

class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'







