#%% Importing libraries

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pandas as pd
import demoji
demoji.download_codes()
from langdetect import detect
import re
import numpy as np # linear algebra
import os
from collections import deque
import scipy
from textblob import TextBlob
from sklearn import metrics
from mlxtend.plotting import plot_confusion_matrix
import nltk
nltk.download("stopwords")
nltk.download("punkt")
from nltk.corpus import stopwords
from nltk import word_tokenize
import string

#%% Starting API
DEVELOPER_KEY = "AIzaSyDxvK0xAoc0wGfKWnWMWZy8JMiA8I-VUiE"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# creating Youtube Resource Object
service = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                                        developerKey = DEVELOPER_KEY)

#%% Video search

query = 'https://www.youtube.com/watch?v=V7dTulDOw4M'

query_results = service.search().list(part = 'snippet', q = query,
                                      order = 'relevance', 
                                      type = 'video',
                                      relevanceLanguage = 'en',
                                      safeSearch = 'moderate').execute()

#%% Extract results

video_id = deque()
channel = deque()
video_title = deque()
video_desc = deque()
for item in query_results['items']:
    video_id.append(item['id']['videoId'])
    channel.append(item['snippet']['channelTitle'])
    video_title.append(item['snippet']['title'])
    video_desc.append(item['snippet']['description'])

#%% Choose the video of interest

video_id = video_id[0]
channel = channel[0]
video_title = video_title[0]
video_desc = video_desc[0]

#%% Extract video information

video_id_pop = deque()
channel_pop = deque()
video_title_pop = deque()
video_desc_pop = deque()
comments_pop = deque()
comment_id_pop = deque()
reply_count_pop = deque()
like_count_pop = deque()

nextPage_token = None

while 1:
  response = service.commentThreads().list(
                    part = 'snippet',
                    videoId = video_id,
                    maxResults = 100, 
                    order = 'relevance', 
                    textFormat = 'plainText',
                    pageToken = nextPage_token
                    ).execute()


  nextPage_token = response.get('nextPageToken')
  for item in response['items']:
      comments_pop.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])
      comment_id_pop.append(item['snippet']['topLevelComment']['id'])
      reply_count_pop.append(item['snippet']['totalReplyCount'])
      like_count_pop.append(item['snippet']['topLevelComment']['snippet']['likeCount'])
        
      video_id_pop.append(video_id)
      channel_pop.append(channel)
      video_title_pop.append(video_title)
      video_desc_pop.append(video_desc)

  if nextPage_token is  None:
    break

output_dict = {
        'Channel': channel_pop,
        'Video Title': video_title_pop,
        'Video Description': video_desc_pop,
        'Video ID': video_id_pop,
        'Comment': comments_pop,
        'Comment ID': comment_id_pop,
        'Replies': reply_count_pop,
        'Likes': like_count_pop,
        }

output_df = pd.DataFrame(output_dict, columns = output_dict.keys())

#%% Erase duplicate comments

unique_df = output_df.drop_duplicates(subset=['Comment'])
comments = unique_df

#%% Erase emojis and filter english comments

comments['clean_comments'] = comments['Comment'].apply(lambda x: demoji.replace(x,""))
comments['language'] = 0
count = 0
for i in range(0,len(comments)):


  temp = comments['clean_comments'].iloc[i]
  count += 1
  try:
    comments['language'].iloc[i] = detect(temp)
  except:
    comments['language'].iloc[i] = "error"
english_comm = comments[comments['language'] == 'en']
en_comments = english_comm

#%% Erase special characters

regex = r"[^0-9A-Za-z'\t]"
copy = en_comments.copy()
copy['reg'] = copy['clean_comments'].apply(lambda x:re.findall(regex,x))
copy['regular_comments'] = copy['clean_comments'].apply(lambda x:re.sub(regex,"  ",x))

#%% Filter info

dataset = copy[['Video ID','Comment ID','regular_comments', 'Likes']].copy()
dataset = dataset.rename(columns = {"regular_comments":"comments"})

#%% Polarity the dataset with TextBlob

data = dataset
data['polarity'] = data['comments'].apply(lambda x: TextBlob(x).sentiment.polarity)
data = data.sample(frac=1).reset_index(drop=True)

#%% Classify the dataset

data['pol_cat']  = 0
data['pol_cat'][data.polarity > 0] = 1
data['pol_cat'][data.polarity <= 0] = 0

data_pos = data[data['pol_cat'] == 1]
data_pos = data_pos.reset_index(drop = True)
data_neg = data[data['pol_cat'] == 0]
data_neg = data_neg.reset_index(drop = True)

#%% Lower the letters and erase the stop-words

data['comments'] = data['comments'].str.lower()
stop_words = set(stopwords.words('english'))
data['comments'] = data['comments'].str.strip()

train = data.copy()
train['comments'] = train['comments'].str.strip()
data['stop_comments'] = data['comments'].apply(lambda x : remove_stopwords(x))

#%% Export the classified dataset

data.to_csv('Dataset-with-sentiments.csv', index = False)

#%% Function to remove stop-words

def remove_stopwords(line):
    word_tokens = word_tokenize(line)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    return " ".join(filtered_sentence)
