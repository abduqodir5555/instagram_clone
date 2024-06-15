from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission

from posts.models import CommentLike, Comment


class IsAuthorOfComment(BasePermission):
    def has_permission(self, request, view):
        commentlike_id = view.kwargs['pk']
        try:
            obj = CommentLike.objects.get(id=commentlike_id)
        except:
            raise ValidationError({"status":False, "message":"Comment like not found!!!"})
        if obj.author == request.user:
            return True
        else:
            return False


