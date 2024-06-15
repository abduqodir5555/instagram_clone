from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework.views import APIView

from .models import Post, PostLike, Comment, CommentLike
from .paginations import CustomPagination
from .permissions import IsAuthorOfComment
from .serializers import PostSerializer, PostLikeSerializer, CommentSerializer, CommentLikeSerializer


class PostListApiView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny, ]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all()


class PostCreateApiView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        serializer.save(author = self.request.user)


class PostRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.serializer_class(instance=post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'status': True,
                'code': status.HTTP_200_OK,
                'message': 'Successfully updated',
                'data': serializer.data
            }
        )

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        return Response(
            {
                'status': True,
                'code': status.HTTP_204_NO_CONTENT,
                'message': 'Successfully deleted!!!',
            }
        )


class PostCommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        return Comment.objects.filter(post_id=post_id)


class PostCommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        serializer.save(author=self.request.user, post_id=post_id)


class PostLikeListView(generics.ListAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        post_id = self.kwargs.get('pk')
        query = PostLike.objects.filter(post_id=post_id)
        return query


class CommentRetrieveApiView(generics.RetrieveAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny, ]
    queryset = Comment.objects.all()


class CommentLikeListView(generics.ListAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        comment_id = self.kwargs.get('pk')
        query = CommentLike.objects.filter(comment_id=comment_id)
        return query


class CommentLikeView(generics.ListCreateAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        user = self.request.user
        query = CommentLike.objects.filter(author = user)
        return query

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [IsAuthenticated, IsAuthorOfComment]
    queryset = CommentLike.objects.all()


class PostLikingView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            obj = PostLike.objects.create(author=request.user, post_id=kwargs['pk'])
            serializer = PostLikeSerializer(obj)
            data = {
                'status': True,
                'message': 'Postga muvaffaqiyatli like bosildi!!!',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            data = {
                'status': False,
                'message': f"{str(e)}",
                'data': None
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            obj = PostLike.objects.get(author=request.user, post_id=pk)
            obj.delete()
            data = {
                'status': True,
                'message': 'LIKE o\'chirildi',
                'data': None
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            data = {
                'status': False,
                'message': f"{str(e)}",
                'data': None
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

