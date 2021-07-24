#import the library 
from pytube import YouTube
#ask user to type in the link 
link = input("Enter the link of youtube video:  ")
#creating an object
yt = YouTube(link)
#to get the highest resolution
ys = yt.streams.get_highest_resolution()
#show the message until downloading
print("Downloading...")
#specifying the location for this video 
ys.download("Downloads\python")
#show the message when download is completed
print("Download completed!!")

# Coded with 💙 by Mr. Unity Buddy
