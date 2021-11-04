from apiclient.discovery import build
import pandas as pd

import os

# Arguments that need to passed to the build function
DEVELOPER_KEY = "AIzaSyCyzN8UJPFeRxfbSH54WaOiZxRon1sR8bk"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# creating Youtube Resource Object
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                                        developerKey = DEVELOPER_KEY)


def video_comments(video_id):


    # Open ro creates the csv with the information
    if os.path.isfile('comentarios.xlsx'):
        comments = pd.read_excel('comentarios.xlsx', index_col=0)
    else:
        comments = pd.DataFrame(columns=['Video', 'Comment',
            'Replies'])


    # empty list for storing reply
    replies = []

    # retrieve youtube video results
    video_response=youtube.commentThreads().list(
    part='snippet,replies',
    videoId=video_id
    ).execute()

    cont = 0

    # iterate video response
    while video_response:

        # extracting required info
        # from each result object
        for item in video_response['items']:

            # Extracting comments
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']

            # counting number of reply of comment
            replycount = item['snippet']['totalReplyCount']

            # if reply is there
            if replycount>0:

                # iterate through all reply
                for reply in item['replies']['comments']:

                    # Extract reply
                    reply = reply['snippet']['textDisplay']

                    # Store reply is list
                    replies.append(reply)

            # print comment with list of reply
            # print(comment, replies, end = '\n\n')

            # Saves the information to a DataFrame
            comments = comments.append({'Video':video_id,
                'Comment':comment, 'Replies':replies}, ignore_index=True)

            # empty reply list
            replies = []
            cont += 1
            print(cont)

            if (cont % 5000 == 0):
                comments.to_excel(f'comentarios_{str(cont)}.xlsx')


            if (cont == 500):
                comments.to_excel(f'comentarios_{str(cont)}.xlsx')
                exit()

        # Again repeat
        if 'nextPageToken' in video_response:
            video_response = youtube.commentThreads().list(
                    part = 'snippet,replies',
                    videoId = video_id
                ).execute()
        else:
            print(comments)
            comments.to_excel('comentarios.xlsx')
            break

    comments.to_excel('comentarios.xlsx')

# Enter video id
video_id = "MwpMEbgC7DA"

# Call function
video_comments(video_id)


