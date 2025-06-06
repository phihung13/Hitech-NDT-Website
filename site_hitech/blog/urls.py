from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_results, name='search_results'),
    path('', views.blog_list, name='blog_list'),
    path('<int:post_id>/', views.blog_detail, name='blog_detail'),
    path('<slug:category_slug>/', views.blog_category, name='blog_category'),  # Đã bỏ 'category/'
    path('tag/<slug:tag_slug>/', views.blog_tag, name='blog_tag'),
    path('search/', views.blog_search, name='blog_search'),
    path('comment/<int:post_id>/', views.post_comment, name='post_comment'),
]