import graphene
from django.db import IntegrityError
from notifications import models as notification_models
from . import models, types


class LikeImage(graphene.Mutation):

    """ Like an Image """

    class Arguments:
        imageId = graphene.Int(required=True)

    Output = types.LikeImageResponse

    def mutate(self, info, **kwargs):
        imageId = kwargs.get('imageId')
        user = info.context.user
        ok = True
        error = None
        if user.is_authenticated:
            try:
                image = models.Image.objects.get(id=imageId)
            except models.Image.DoesNotExist:
                error = 'Image Not Found'
                return types.LikeImageResponse(ok=not ok, error=error)

            try:
                like = models.Like.objects.create(
                    creator=user, image=image)
                return types.LikeImageResponse(ok=ok, error=error)
            except IntegrityError as e:
                print(e)
                error = "Can't Like Image"
                return types.LikeImageResponse(ok=not ok, error=error)

            try:
                notification_models.Notification.objects.create(
                    actor=user, target=image.creator, verb="like", payload=image)
            except IntegrityError as e:
                print(e)
                pass

        else:
            error = 'You need to log in'
            return types.LikeImageResponse(ok=not ok, error=error)


class UnlikeImage(graphene.Mutation):

    """ Unlike an Image """

    class Arguments:
        imageId = graphene.Int(required=True)

    Output = types.UnlikeImageResponse

    def mutate(self, info, **kwargs):
        imageId = kwargs.get('imageId')
        user = info.context.user
        ok = True
        error = None
        if user.is_authenticated:
            try:
                image = models.Image.objects.get(id=imageId)
            except models.Image.DoesNotExist:
                error = 'Image Not Found'
                return types.LikeImageResponse(ok=not ok, error=error)

            try:
                like = models.Like.objects.get(
                    creator=user, image=image)
                like.delete()
                return types.LikeImageResponse(ok=ok, error=error)
            except models.Like.DoesNotExist:
                pass

            try:
                notification = notification_models.Notification.objects.get(
                    actor=user, target=image.creator, verb="like", payload=image)
                notification.delete()
            except notification_models.Notification.DoesNotExist:
                pass

        else:
            error = 'You need to log in'
            return types.LikeImageResponse(ok=not ok, error=error)


class AddComment(graphene.Mutation):

    """ Add Comment """

    class Arguments:
        imageId = graphene.Int(required=True)
        message = graphene.String(required=True)

    Output = types.AddCommentResponse

    def mutate(self, info, **kwargs):
        imageId = kwargs.get('imageId')
        message = kwargs.get('message')

        user = info.context.user

        ok = True
        error = None
        comment = None

        if user.is_authenticated:
            try:
                image = models.Image.objects.get(id=imageId)
            except models.Image.DoesNotExist:
                error = 'Image Not Found'
                return types.AddCommentResponse(ok=not ok, error=error, comment=comment)

            try:
                comment = models.Comment.objects.create(
                    message=message, image=image, creator=user)
                return types.AddCommentResponse(ok=ok, error=error, comment=comment)
            except IntegrityError as e:
                print(e)
                error = "Can't create the comment"
                return types.AddCommentResponse(ok=not ok, error=error, comment=comment)
        else:
            error = 'You need to log in'
            return types.AddCommentResponse(ok=not ok, error=error, comment=comment)


class DeleteComment(graphene.Mutation):

    class Arguments:
        imageId = graphene.Int(required=True)
        commentId = graphene.Int(required=True)

    Output = types.DeleteCommentResponse

    def mutate(self, info, **kwargs):
        imageId = kwargs.get('imageId')
        commentId = kwargs.get('commentId')

        user = info.context.user

        ok = True
        error = None

        if user.is_authenticated:

            try:
                image = models.Image.objects.get(id=imageId)
            except models.Image.DoesNotExist:
                error = 'Image Not Found'
                return types.DeleteCommentResponse(ok=not ok, error=error)

            try:
                comment = models.Comment.objects.get(id=commentId)
            except models.Comment.DoesNotExist:
                error = 'Comment Not Found'
                return types.DeleteCommentResponse(ok=not ok, error=error)

            if comment.creator.id == user.id or image.creator.id == user.id:
                comment.delete()
            else:
                error = "Can't Delete Comment"
            return types.DeleteCommentResponse(ok=not ok, error=error)

        else:
            error = 'You need to log in'
            return types.DeleteCommentResponse(ok=not ok, error=error)


class EditImage(graphene.Mutation):

    class Arguments:

        imageId = graphene.Int(required=True)
        caption = graphene.String()
        location = graphene.String()

    Output = types.EditImageResponse

    def mutate(self, info, **kwargs):

        user = info.context.user
        imageId = kwargs.get('imageId')

        ok = True
        error = None

        if user.is_authenticated:

            try:
                image = models.Image.objects.get(id=imageId)
            except models.Image.DoesNotExist:
                error = "Image Not Found"
                return types.EditImageResponse(ok=not ok, error=error)

            if image.creator.id != user.id:

                error = "Unauthorized"
                return types.EditImageResponse(ok=not ok, error=error)

            else:

                try:

                    caption = kwargs.get('caption', image.caption)
                    location = kwargs.get('location', image.location)

                    image.caption = caption
                    image.location = location

                    image.save()
                    return types.EditImageResponse(ok=ok, error=error, image=image)

                except IntegrityError as e:
                    print(e)
                    error = "Can't Save Image"
                    return types.EditImageResponse(ok=not ok, error=error)

        else:
            error = 'You need to log in'
            return types.EditImageResponse(ok=not ok, error=error)


class DeleteImage(graphene.Mutation):

    class Arguments:
        imageId = graphene.Int(required=True)

    Output = types.DeleteImageResponse

    def mutate(self, info, **kwargs):

        user = info.context.user
        imageId = kwargs.get("imageId")

        ok = True
        error = None

        if user.is_authenticated:

            try:
                image = models.Image.objects.get(id=imageId)
            except models.Image.DoesNotExist:
                error = "Image Not Found"
                return types.DeleteImageResponse(ok=not ok, error=error)

            if image.creator.id == user.id:

                image.delete()

                return types.DeleteImageResponse(ok=ok, error=error)

            else:

                error = "Unauthorized"
                return types.DeleteImageResponse(ok=not ok, error=error)

        else:
            error = "Unauthorized"
            return types.DeleteImageResponse(ok=not ok, error=error)


class UploadImage(graphene.Mutation):

    class Arguments:

        fileUrl = graphene.String(required=True)
        caption = graphene.String(required=True)
        location = graphene.String()

    Output = types.UploadImageResponse

    def mutate(self, info, **kwargs):

        user = info.context.user

        ok = True
        error = None

        fileUrl = kwargs.get('fileUrl')
        caption = kwargs.get('caption')
        location = kwargs.get('location')

        if user.is_authenticated:

            try:
                image = models.Image.objects.create(
                    creator=user, caption=caption, location=location, file=fileUrl)
                return types.UploadImageResponse(ok=ok, error=error, image=image)
            except IntegrityError as e:
                print(e)
                error = "Can't Create Image"
                return types.UploadImageResponse(ok=not ok, error=error)

        else:

            error = "Unauthorized"
            return types.UploadImageResponse(ok=not ok, error=error)
