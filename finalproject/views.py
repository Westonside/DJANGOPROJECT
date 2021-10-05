from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import *
from django.db import IntegrityError
import yfinance as yf
from googlesearch import search
from yahoo_finance import *
import requests
import json
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def index(request):
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse("login"))
    return render(request, "finalproject/index.html")


def logIn(request):
    if request.method == "POST":
        userName = request.POST["username"]
        passWord = request.POST["password"]

        user = authenticate(request, username = userName, password = passWord)

        #if there is a user under that
        if user is not None:
            login(request,user)
            return HttpResponseRedirect(reverse("index"))
        else:
            print("invalid")
            return HttpResponse("invalid")
    else:
        return render(request, "finalproject/login.html")


def logOut(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

            


def register(request):
    if request.method == "POST":
        userName = request.POST["username"]
        passWord = request.POST["password"]
        email = request.POST["email"]
        confirmation = request.POST["confirmation"]
        print(userName)
        print(passWord)
        print(confirmation)
        if passWord != confirmation:
            return render(request, "finalproject/register.html", {
                "message": "Passwords do not match!"
            })
        try:
            user = User.objects.create_user(userName, email, passWord)
            user.save()
            login(request,user)
            return HttpResponseRedirect(reverse("index"))
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
      
    else:
        return render(request,"finalproject/register.html")


def getStocks(request):
    #something
    print('something')
    stocks = StockFollow.objects.filter(followingUser = request.user).first()
    
    print(stocks)
    if stocks is None:
        return JsonResponse(json.dumps({"success":False}), safe = False)
    return JsonResponse(stocks.serialize(), safe = False)



@csrf_exempt
def changeStock(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        print(data["stocks"])
        stocks = data["stocks"]
        splitUp = stocks.split(',')
        allStock = []
        for i in splitUp:
            try:
                something = yf.Ticker(i)
                print(something.info)
                allStock.append(i)
            except:
                #nothing,skip the ticker that does not exist
                print("not a valid stock")
        # print(",".join(allStock))
        
        stored =""
        print(allStock)
        allStock = allStock[0:5] if len(allStock) > 5 else allStock
        print(len(allStock))
        if len(allStock) == 0:
            return JsonResponse({"success": False})
        else:
            #check if the user already follows any stocks
            existing = StockFollow.objects.filter(followingUser = request.user).first()
            if existing is not None:
                print(existing)
                existing.delete()
                print("there is an existing record", existing)
            stock = ",".join(allStock)
            print(stocks)
            saved = StockFollow(followingUser=request.user, stocks=stock)
            saved.save()
            print('saved', saved)

    return JsonResponse({"success": True})

@login_required
def getPosts(request,section):
    print('getting all the posts, the user will send how many that they want ')
    #get the starting part point of posts that the user wants default at 0 if the user does not specify a starting point
    start = int(request.GET.get("start") or 0)
    end = int(request.GET.get("end") or (start+9))
    print("start", start, "end", end)

    if section =="all":
        posts = Post.objects.all()

    posts = posts.order_by("-timestamp").all()
    print(posts)
    print(posts[0:9], 'cock and ball torture')
    posts = posts[start:end]
    print(posts)

    return JsonResponse([post.serialize(request) for post in posts], safe = False)

@csrf_exempt
@login_required
def postPost(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        print("put", data)
        editPost = Post.objects.filter(pk=data['id'])
        editPost.update(content=data['content'])
        print(editPost)
        print(editPost)
        return JsonResponse({'success': True})
    elif request.method =="POST":
        data = json.loads(request.body)
        post = Post(theUser = request.user,content = data['content'])
        post.save()
        print('post has been saved')
        return JsonResponse({'success': True})
    else:
        return JsonResponse({"success": False}, status = 403)

@csrf_exempt
def likePost(request):
    if request.method != "POST":
        return JsonResponse({"success": False}, status = 403)
    
    data = json.loads(request.body)
    #check if the user has already liked the post
    postLikeCheck = Likes.objects.filter(postId = data['postId'], likeUser = request.user)
    
    print(postLikeCheck)
    #if they have like the post before then change their like status
    if len(postLikeCheck) == 0:
        print('new like')
        newLike = Likes(postId = Post.objects.filter(pk=data['postId']).first(), likeUser = request.user, liked = True)
        newLike.save()
        return JsonResponse({'success': True})
    else:
        other = postLikeCheck.first()
        opposite = not(other.liked)
        
        postLikeCheck.update(liked = opposite)
        return JsonResponse({'success': True})
        #if the user has already liked in the past then set the value of the last saved like to be !