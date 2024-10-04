from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings 
import json
import os
from pytube import YouTube
import assemblyai as aai
import openai
from .models import BlogPost

# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html' )

@csrf_exempt
def generate_blog(request):
   if request.method == 'POST':
       try:
           data = json.loads(request.body)
           yt_link = data['link']
       except(KeyError, json.JSONDecodeError):
           return JsonResponse({'error': 'invalid data sent'}, status=400)
       
        # Get youtube title
       tittle = yt_tittle(yt_link)
   
        # get transcript
       transcription = get_transcription
       if not transcription:
            return JsonResponse({'error': "Failed to get transcript"}, status=500)
   
        # get openAI to generate the blog post
       blog_content = generate_blog_from_transcription(transcription)
       if not blog_content:
            return JsonResponse({'error': "Failed to generate blog article"}, status=500)
   
        # save blog article to database
       new_blog_article = BlogPost.objects.create(
           user=request.user,
           youtube_tittle=tittle,
           youtube_link=yt_link,
           generated_content=blog_content,
       )
       new_blog_article.save()
   
        # return blog article as a response
       return JsonResponse({'content':blog_content})
   else:
       return JsonResponse({'error': 'Invalid requset method'}, status=405)
   
   
def yt_tittle(link):
       yt = YouTube(link)
       tittle = yt_tittle
       return tittle
   
def download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    return new_file
def get_transcription(link):
    audio_file = download_audio()
    aai.settings.api_key = "568487c1a0724e06979d28d536e1257b"
    
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    
    return transcript.text
def generate_blog_from_transcription(transcription):
    openai.api_key="sk-QNXysKeCX0YgCNTp2J59LYIUWyZufo0-tZQFmHsP7vT3BlbkFJDDTn1XVd_hRiAOcMhu_Pvr5pdqPVU7EgEyztyr8soA"
    
    prompt = f"Based on the following transcript from a Youtube video, write a comprhensive blog article, write it based on the transcript, but do not make it look like a youtube video, make it look like a proper blog article: \n\n{transcription}\n\nArticle:"
    
    response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=1000
    )
    
    generated_content = response.choices[0].text.strip()
    
    return generated_content

def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, "all-blogs.html", {'blog_articles': blog_articles})

def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
    else:
        return redirect('/')
    
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatpassword = request.POST['repeatpassword']
        
        if password == repeatpassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creating account'
                return render(request, 'signup.html', {'error_message':error_message})
            
        else:
            error_message = 'Password do not match'
            return render(request, 'signup.html', {'error_message':error_message})
        
    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')