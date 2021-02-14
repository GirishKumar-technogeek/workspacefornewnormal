from django.shortcuts import render,redirect
from django.contrib import auth
from django.http import JsonResponse,HttpResponse
import math,random
from django.conf import settings 
from django.core.mail import send_mail
import requests
from .RecSys import RecSys
from .models import *
# Create your views here.

def home(request):
    return render(request,'accounts/home.html')

def mask(request):
    return render(request,'otherapps/mask.html')

def rec_foods(request):
    if request.method == 'POST':
        timeframe  = request.POST['timeframe']
        targetCalories = request.POST['targetCalories']
        diet = request.POST['diet']
        url = 'https://api.spoonacular.com/mealplanner/generate?apiKey=620c49dbdc9b473587c8e30cde6214dd&timeFrame=' + timeframe +'&targetCalories=' + str(targetCalories) +'&diet=' + diet
        response = requests.get(url).json()['meals']
        context = {'response':response,'timeframe':timeframe,'targetCalories':targetCalories,'diet':diet}
        return render(request,'otherapps/sendfood.html',context)
    else:
        return render(request,'otherapps/getfood.html')

def rec_books(request):
    if request.method == 'POST':
        title = request.POST['title']
        url = 'https://www.googleapis.com/books/v1/volumes?q=' + title + '&key=AIzaSyAxPLOBKyY5prSNtxOZ1uWBrnrv0Tr3DyQ'
        response = requests.get(url).json()['items']
        context = {'response':response,'title':title}
        return render(request,'otherapps/sendbook.html',context)
    else:
        return render(request,'otherapps/getbook.html')

def send_news(request):
    if request.method == 'POST':
        search = request.POST['search']
        url = 'https://newsapi.org/v2/everything?q=' + search + '&apiKey=6606c63a8a9444089c11f85e11aae164'
        response = requests.get(url).json()['articles']
        context = {'response':response,'search':search}
        return render(request,'otherapps/sendnews.html',context)
    else:
        return render(request,'otherapps/getnews.html')

def startCall(request):
    url = "https://api.daily.co/v1/rooms"
    payload = {"properties": {
    "max_participants": 10,
    "enable_chat": True,
    "enable_screenshare": True
    }}
    headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer 93439dbf79eca1da9fe23cd0851a574028c8439aa7880dab4dbd34a4018ed408"
    }
    response = requests.request("POST", url,json=payload,headers=headers).json()
    return redirect(response['url'])

def index(request):
    return render(request, 'otherapps/index.html')


def show_results(request):
	keywords = request.GET['keywords']
	limit = int(request.GET['limit'])
	model = RecSys()
	results = model.recommended(keywords=keywords, mode='jobs')
	context = {
		'results': results[:limit]
	}
	return render(request, 'otherapps/search.html', context)

            