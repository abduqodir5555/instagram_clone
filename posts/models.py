from django.core.validators import FileExtensionValidator, MaxLengthValidator
from django.db import models
from django.db.models import UniqueConstraint

from common.models import BaseModel
from users.models import User


class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='related_posts')
    image = models.ImageField(upload_to='posts/', validators=[FileExtensionValidator(
        allowed_extensions=['jpg', 'jpeg', 'png']), ])
    caption = models.TextField(validators=[MaxLengthValidator(2000)])

    def __str__(self):
        return f"{self.author} | post about > {self.caption[:80]}"

    class Meta:
        db_table = 'posts'
        verbose_name = 'post'
        verbose_name_plural = 'posts'


class Comment(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='related_comment_authors')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='related_comment_posts')
    comment = models.TextField(validators=[MaxLengthValidator(2000)])
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='child', null=True, blank=True)

    def __str__(self):
        return f"{self.author} | comment about > {self.comment[:80]}"

    class Meta:
        db_table = 'comments'
        verbose_name = 'comment'
        verbose_name_plural = 'comments'


class PostLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='related_postlikes_authors')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='related_postlike_posts')

    class Meta:
        db_table = 'postlikes'
        verbose_name = 'postlike'
        verbose_name_plural = 'Postlikes'
        constraints = [
            UniqueConstraint(
                fields=['author', 'post'],
                name='Bir postga qayta like bosib bo\'lmaydi'
            )
        ]


class CommentLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='related_commentlikes_authors')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='related_commentlike_comments')

    class Meta:
        db_table = 'commentlike'
        verbose_name = 'commentlike'
        verbose_name_plural = 'Commentlikes'
        constraints = [
            UniqueConstraint(
                fields=['author', 'comment'],
                name='Bir commentga qayta like bosib bo\'lmaydi!!!'
            )
        ]
