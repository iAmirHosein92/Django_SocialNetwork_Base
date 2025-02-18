from django.urls import path
from . import views

app_name = 'home'
urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('post_create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/detail/<int:post_id>/<slug:post_slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/update/<int:post_id>/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/delete/<int:post_id>/', views.PostDeleteView.as_view(), name='post_delete'),
    path('like/<int:post_id>/', views.PostLikeView.as_view(), name='post_like'),
    path('reply/<int:post_id>/<int:comment_id>', views.PostAddReplyView.as_view(), name='add_reply'),

]