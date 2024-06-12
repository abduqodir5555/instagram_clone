from rest_framework import serializers

from posts.models import Post, PostLike, Comment, CommentLike
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'photo')


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    post_likes_count = serializers.SerializerMethodField('get_post_likes_count')
    post_comments_count = serializers.SerializerMethodField('get_post_comments_count')
    me_liked = serializers.SerializerMethodField('get_me_liked')

    class Meta:
        model = Post
        fields = ('id',
                  'author',
                  'image',
                  'caption',
                  'created_time',
                  'post_likes_count',
                  'post_comments_count',
                  'me_liked'
                  )

    @staticmethod
    def get_post_likes_count(obj):
        return obj.related_postlike_posts.count()

    @staticmethod
    def get_post_comments_count(obj):
        return obj.related_comment_posts.count()

    def get_me_liked(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            return obj.related_postlike_posts.filter(author=request.user).exists()
        else:
            return False


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField('get_replies')
    me_liked = serializers.SerializerMethodField('get_me_liked')
    likes_count = serializers.SerializerMethodField('get_likes_count')

    class Meta:
        model = Comment
        fields = ('id', 'author', 'comment', 'parent', 'created_time', 'replies', 'me_liked', 'likes_count')

    def get_replies(self, obj):
        if obj.child.exists():
            just = self.__class__(obj.child.all(), many=True, context=self.context)
            return just.data
        else:
            return None

    def get_me_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.related_commentlike_comments.filter(author=user).exists()
        else:
            return False

    @staticmethod
    def get_likes_count(obj):
        return obj.related_commentlike_comments.count()


class CommentLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = CommentLike
        fields = ('id', 'author', 'comment')


class PostLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ('id', 'author', 'post')
