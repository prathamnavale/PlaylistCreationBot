# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 18:24:47 2024

@author: saish
"""

from flask import Flask, request, jsonify
import openai
import spotipy
import os

from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

#Set up for Spotify API and OpenAI API
os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"
openai.api_key  = os.getenv('OPENAI_API_KEY')
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(  
    client_id = 'SPOTIFY_CLIENT_ID',
    client_secret='SPOTIFY_CLIENT_SECRET',
    redirect_uri='http://localhost/?code=AQC7nRnVGu1o0yYIBzpdXRIvtHiK4OJlFYLo_HSQRHxccbyuQ3OdJV5Lw9jDdWETbV6PAOUVTZbuSRSzB-O-0Z8XDbB_QyXihtOLfaiScpMAZmfdwaVRwSu5U1BXBqQ0mxgZzzqYIgqIM1oGUNv1gYzC-uGh6JkhtpQ4PIcDuLrh8LOOh1-ckAxPNxHn',
    scope='playlist-modify-public'
    ))

#Set up for open ai completions

def get_completion(prompt,model= "gpt-4o-mini"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content
#Set up for context based chat with bot

def get_completion_from_messages (messages, model="gpt-4o-mini", temperature=0):
    
    user_message = input
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature, 
    ) 
    return response.choices[0].message.content




context = [{'role':'system', 'content': """"You are a Utility bot for spotify users that makes playlists for them. You first greet the user, \
            then ask what they would like to name their custom playlist. Once they have provided their playlist name, tell them you can add songs to their playlist, reccomend songs and add them to their playlist, add songs that fit a certain vibe or are a part of a certain genere. Tell the user they should say done when they are done deciding what songs they want to add to the playlist. List out all the songs the user wants to add to the playlist as the conversation continues. Make sure you have both the name and the artists of each song in every scenario. Tell them to say done whenever they are done with what they want to add. At the end of the conversation show a list of all songs that will be in the playlist.""" }]
messages = context.copy()


#Finds tracks in spotify to add to playlist

def get_uri(artist,name):
    query = f"artist:{artist} track:{name}"
    result = sp.search(q = query, type = 'track', limit = 1)
    tracks = result['tracks']['items']
    if tracks:
        return tracks[0]['uri']
    else:
        print(f"Track '{name}' by {artist} not found.")
        return None
    
#Creates spotify playlist

def create_playlist(name,songs):
    """
    Create a Spotify playlist with the given name and add the specified tracks to it.
    """
    user_id = sp.current_user()["id"]
    playlist = sp.user_playlist_create(user=user_id, name=name, public=True)
    pid = playlist['id']
    track_uris = []
    for artist, title in songs:
        uri = get_uri(artist,title)
        if uri:
            track_uris.append(uri)
    if not track_uris:
        print("No tracks were given to me")
        return
    sp.playlist_add_items(playlist_id= pid, items = track_uris)
    print(f"Added {len(track_uris)} tracks to the playlist.")
    

#Gets the desired name of the playlist from the conversation with the user    
    
def get_title(messages):
    prompt = prompt = f"""
Your task is to return just the playlist title from the conversation given. \


Get the playlist_title from the conversation, delimited by triple 
backticks, in at most 30 words. 

Review: ```{messages}```
"""
    response = get_completion(prompt)
    return response


#Gets the exact song names from the conversation with the bot
def get_song_names(messages):
    prompt = prompt = f"""
Your task is to return all the song names from the conversation in a list separated by commas. \


Get the song names from the list of songs in the numbered list at the very end of the conversation only include the title of the song not the artist, make sure it is in the order of first mentioned to last,the conversation is delimited by triple 
backticks. 

Review: ```{messages}```
"""
    response = get_completion(prompt)
    song_list = response.split(', ')
    return song_list

#Gets the exact name of each artist for the songs desired.
def get_song_artists(messages):
    prompt = prompt = f"""
Your task is to make a list of artists of the songs from the conversation in a list separated by commas . \
    

if the artist is the same for any of the songs repeat the artist name in the list for example if there are two songs by the same artist the list would look like this artist, artist \
    
there should be an equal amount of artists in the list to the number of songs  \


Get a list of the song artists from the list of songs in the numbered list at the very end of the conversation , the conversation is delimited by triple 
backticks. 

Review: ```{messages}```
"""
    response = get_completion(prompt)
    print(response)
    artist_list = response.split(', ')
    
    return artist_list     
def main():
    
#Runs the chatbot
    while True:
        
        user_input = input("You: ")
        # Get a response from the AI
        print("AI is thinking...")
        #changed role from system to user
        messages.append({'role': 'user', 'content': str(user_input)})
        ai_response = get_completion_from_messages(messages,temperature = 1)
        messages.append({'role': 'system', 'content': str(ai_response)})
        print(f"AI: {ai_response}")
        #Creates the playlist using desired specifications
        if user_input == "Done":    
            x = get_song_artists(messages)
            y = get_song_names(messages)  
            songs = list(zip(get_song_artists(messages),get_song_names(messages)))
            print(x)
            print(y)
            print(songs)
            create_playlist(get_title(messages),songs)
            break
if __name__ == "__main__":
    main()
