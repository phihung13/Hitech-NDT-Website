from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('search/', views.search_results, name='search_results'),
    path('tag/<slug:tag_slug>/', views.blog_tag, name='blog_tag'),
    path('post/comment/<int:post_id>/', views.post_comment, name='post_comment'),
    
    # Blog management URLs - Đặt trước URL có slug để tránh conflict
    path('create/', views.create_post, name='create_post'),
    path('edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    
    # URL có slug - đặt cuối cùng
    path('<slug:category_slug>/', views.blog_category, name='blog_category'),
    path('<slug:category_slug>/<slug:post_slug>/', views.blog_detail, name='blog_detail'),
]