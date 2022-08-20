from flask import Flask, render_template, request
import instaloader
import pandas as pd
import os
import sys
import json
from urllib import response
import requests
from apiclient.discovery import build
import time
import re
import numpy as numpy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plot
from matplotlib import pyplot as plt
import nltk

L = instaloader.Instaloader()

app = Flask(__name__)

@app.route('/')
def index ():
    hometitle = 'SVLAD SCRAPER'
    return render_template('index.html', hometitle=hometitle)

@app.route('/igscraper')
def igscraper ():
    igtitle = 'Instagram Scrapper'
    return render_template('igscraper.html', igtitle=igtitle)

@app.route('/ytscraper')
def ytscraper ():
    yttitle = 'Youtube Scrapper'
    return render_template('ytscraper.html', yttitle=yttitle)

@app.route('/analysis')
def analysis ():
    anatitle = 'Sentiment Analysis'
    return render_template('analysis.html', anatitle=anatitle)


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/compareig', methods=['POST'])
def ig ():
    
    user_login = request.form['user_login']
    user_pass = request.form['user_pass']
    L.login(user_login, user_pass)
    data = request.form['ig_user']
    username = data
    profile = instaloader.Profile.from_username(L.context, username)
       
    usernamelist = [None]
    captionlist = [None]
    hashtaglist = [None]
    likeslist = [None]
    commentlist = [None]
    followerlist = [None]
    for post in profile.get_posts():
        caption = post.caption
        if caption is None:
            caption = ""
        if caption is not None:
            caption = caption.encode('ascii', 'ignore').decode('ascii')
        hashtag = post.caption_hashtags
        likes = post.likes
        
        comments = []
        for comment in post.get_comments() :
            comments.append(comment.text.encode('ascii', 'ignore').decode('ascii'))

        usernamelist.append(username)
        captionlist.append(caption)
        hashtaglist.append(hashtag)
        likeslist.append(likes)
        commentlist.append(comments)

    pd.options.display.max_colwidth = 100
    data = pd.DataFrame({"Account":usernamelist, "Post":captionlist, "Tag":hashtaglist, "Likes":likeslist,  "Comments":commentlist})
    timestring = time.strftime("%Y%m%d_%H%M%S")
    path =r'static/hasil_ig/'
    nama_file = os.path.join(path, "Dataset_" + username + "_" + timestring + ".csv")
    file_csv = ("Dataset_" + username + "_" + timestring + ".csv")
    data.to_csv(nama_file)

    
    return render_template('display1.html', file_csv=file_csv)

@app.route('/compareyt', methods=['POST'])
def yt (): 
    user_input = request.form['yt_link']
    stdoutOrigin=sys.stdout
    filename = 'log_youtube_'+user_input+'.txt'
    sys.stdout = open(os.path.join('static/hasil_yt/', filename), "w", encoding='utf-8')

    URL = 'https://www.googleapis.com/youtube/v3/'
#Enter API KEY here
    API_KEY = 'AIzaSyARpEA5nl4hw7GFpGlBSO69Np6piY0h3Ho'
#Enter your Video ID here
    VIDEO_ID = (user_input)

    youtube = build('youtube', 'v3', developerKey=API_KEY)


    results = youtube.videos().list(id=VIDEO_ID, part='snippet,statistics').execute()
    for result in results.get('items', []):
        videoID   = print ('Video ID    = ' + result['id'])
        line      = print ('---------------------------------------------------')
        publish   = print ('Publish     = ' + result['snippet']['publishedAt'])
        line      = print ('---------------------------------------------------')
        views     = print ('Views       = ' + result['statistics']['viewCount'])
        line      = print ('---------------------------------------------------')
        likes     = print ('Likes       = ' + result['statistics']['likeCount'])
        line      = print ('---------------------------------------------------')
        #print ('Disliked    :' + result['statistics']['dislikeCount'])
        judul     = print ('Judul       = ' + result['snippet']['title'])
        line      = print ('---------------------------------------------------')
        deskripsi = print ('Deskripsi   =\n'+ result['snippet']['description'])
        line      = print ('---------------------------------------------------')
        comment   = print ('COMENT      = ' + result['statistics']['commentCount'])
        line      = print ('---------------------------------------------------')

    def print_video_comment(video_id, next_page_token):
        params = {
            'key': API_KEY,
            'part': 'snippet',
            'videoId': video_id,
            'order': 'relevance',
            'textFormat': 'plaintext',
        }
        if next_page_token is not None:
            params['pageToken'] = next_page_token
        response = requests.get(URL + 'commentThreads', params=params)
        resource = response.json()

        for comment_info in resource['items']:
            user_name = print("Username     :",comment_info['snippet']['topLevelComment']['snippet']['authorDisplayName'])
            text      = print("Comment      :",comment_info['snippet']['topLevelComment']['snippet']['textDisplay'])
            like_cnt  = print("Comment Like :",comment_info['snippet']['topLevelComment']['snippet']['likeCount'])
            reply_cnt = print("Total Reply  :",comment_info['snippet']['totalReplyCount'])
            parentId  = comment_info['snippet']['topLevelComment']['id']
            print_video_reply(video_id, next_page_token, parentId)
            print('===========================================================')

        if 'nextPageToken' in resource:
            print_video_comment(video_id, resource["nextPageToken"])

    def print_video_reply(video_id, next_page_token, id):
        params = {
            'key': API_KEY,
            'part': 'snippet',
            'videoId': video_id,
            'textFormat': 'plaintext',
            'parentId': id,
        }

        if next_page_token is not None:
            params['pageToken'] = next_page_token
        response = requests.get(URL + 'comments', params=params)
        resource = response.json()

        for comment_info in resource['items']:
            print("==>")
            user_name = print("Username Reply :",comment_info['snippet']['authorDisplayName'])
            text      = print("Reply          :",comment_info['snippet']['textDisplay'])
            like_cnt  = print("Reply Like     :",comment_info['snippet']['likeCount'])

        if 'nextPageToken' in resource:
            print_video_reply(video_id, resource["nextPageToken"], id)

    video_id = VIDEO_ID
    print_video_comment(video_id, None,)

    sys.stdout.close()
    sys.stdout=stdoutOrigin

    return render_template('display2.html', filename=filename)

@app.route('/compareana', methods=['POST'])
def filenama():
    f = request.files['fileana']
    comment1 = f.read().decode('utf-8')
    word_tokens = word_tokenize(comment1)

    stop_words = set(stopwords.words('mode1'))
    stop_words1 = ['bagus', 'sekali', 'enak', 'banget', 'tidak', 'suka', 'recomen']

    word_tokens_no_stopwords1 = dict([(match, len([w for w in word_tokens if match in w])) for match in stop_words1])
    word_tokens_no_stopwords = [w for w in word_tokens if not w in stop_words]

    freq_kata_1 = nltk.FreqDist(word_tokens_no_stopwords1)
    freq_kata_2 = nltk.FreqDist(word_tokens_no_stopwords)

    plt.ioff()
    fig = plt.figure()
    fig.set_figwidth(10)
    fig.set_figheight(10)
  
    freq_kata_1.plot()
    plt.savefig('static/image/foto1.png')
    plt.close(fig)

    plt.ioff()
    fig = plt.figure()
    fig.set_figwidth(15)
    fig.set_figheight(15)

    freq_kata_2.plot(10)
    plt.savefig('static/image/foto2.png')
    plt.close(fig)

    plt.show()

    return render_template('display3.html')
    
if __name__ == "__main__":
    app.run(debug=True)