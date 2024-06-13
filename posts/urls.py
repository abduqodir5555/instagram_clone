from django.urls import path

from .views import PostListApiView, PostCreateApiView, PostRetrieveUpdateDestroyApiView, PostCommentListView, \
    PostCommentCreateView


urlpatterns = [
    path('posts/', PostListApiView.as_view()),
    path('post-create/', PostCreateApiView.as_view()),
    path('post-3in/<uuid:pk>/', PostRetrieveUpdateDestroyApiView.as_view()),
    path('comments/<uuid:pk>/', PostCommentListView.as_view()),
    path('comments/<uuid:pk>/create/', PostCommentCreateView.as_view())
]
