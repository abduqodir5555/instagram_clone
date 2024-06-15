from django.urls import path

from .views import PostListApiView, PostCreateApiView, PostRetrieveUpdateDestroyApiView, PostCommentListView, \
    PostCommentCreateView, PostLikeListView, CommentRetrieveApiView, CommentLikeListView, CommentLikeView, \
    CommentDetailView, PostLikingView


urlpatterns = [
    path('posts/', PostListApiView.as_view()),
    path('post-create/', PostCreateApiView.as_view()),
    path('post-3in/<uuid:pk>/', PostRetrieveUpdateDestroyApiView.as_view()),
    path('comments/<uuid:pk>/', PostCommentListView.as_view()),
    path('comments/<uuid:pk>/create/', PostCommentCreateView.as_view()),
    path('<uuid:pk>/likes/', PostLikeListView.as_view()),
    path('comment/<uuid:pk>/', CommentRetrieveApiView.as_view()),
    path('comment/<uuid:pk>/likes/', CommentLikeListView.as_view()),

    path('comment/likes/', CommentLikeView.as_view()),
    path('comment/likes/<uuid:pk>/', CommentDetailView.as_view()),

    path('post/<uuid:pk>/liking/', PostLikingView.as_view()),
]
