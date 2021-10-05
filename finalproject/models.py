from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass

class StockFollow(models.Model):
    followingUser = models.ForeignKey("User", on_delete= models.CASCADE)
    stocks = models.TextField(blank=True)    

    def __str__(self):
        return(f"user: {self.followingUser} follows stocks: {self.stocks}")

    def serialize(self):
        return{
            "followingUser": self.followingUser.username,
            "stocks": self.stocks,
            "success": True
        }

class Post(models.Model):
    theUser = models.ForeignKey("User", on_delete = models.CASCADE)
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return(f"{self.theUser}: {self.content} posted at{self.timestamp}")

    def serialize(self,request):
        liked = Likes.objects.filter(postId=self.pk, likeUser = request.user, liked=True).first()
        
        return{
            "user": self.theUser.username,
            "content": self.content,
            "timestamp" : self.timestamp.strftime("%b %-d %Y, %-I:%M %p"),
            "canEdit" : request.user.username == self.theUser.username,
            "pk" : self.pk,
            "likes": Likes.objects.filter(postId=self.pk, liked=True).count(),
            "liked": False if liked is None else True if liked.liked is True else False
        }

class Likes(models.Model):
    postId = models.ForeignKey("Post", on_delete = models.CASCADE)
    likeUser = models.ForeignKey("User", on_delete = models.CASCADE, related_name = "liking_user")
    liked = models.BooleanField(default = False)

    def __str__(self):
        return(f"{self.likeUser} liked = {self.liked} the post {self.postId}")