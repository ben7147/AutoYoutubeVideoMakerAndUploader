import requests
from PIL import Image
import os
from io import BytesIO
from PIL import Image, ImageDraw
from moviepy.editor import VideoFileClip, ImageClip
import random
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from oauth2client.client import flow_from_clientsecrets


# pause
def pause():
    programPause = input("Press any key to continue...")


# Saves 140 memes

counter = 1
def SaveMeme(folder):
    global counter  # Use the global counter variable
    
    response = requests.get("https://meme-api.com/gimme")

    if response.status_code != 200:
        print("Failed to fetch meme data.")
        return
    
    meme_data = response.json()
    meme_url = meme_data.get("url")
    meme_title = meme_data.get("title", "Unknown")
    meme_author = meme_data.get("author", "Unknown")

    image_resp = requests.get(meme_url)
    if image_resp.status_code != 200:
        print("Failed to fetch meme image.")
        return
    
    image = Image.open(BytesIO(image_resp.content))

    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, f"meme{counter}.jpg")

    image.convert("RGB").save(file_path, "JPEG")
    print(f"Image saved to {file_path}")
    
    counter += 1

for _ in range(140):
    SaveMeme(folder="memes")


# Convert 2 memes into 1

random_number = 1
counter3 = 1
def ConvertImageTo1(converted_img):
    global random_number
    global counter3

    img1 = Image.open(f"memes/meme{random_number}.jpg")
    random_number2 = random.randint(1, 100)

    if random_number == random_number2:
        random_number2 = random.randint(1, 100)

    img2 = Image.open(f"memes/meme{random_number2}.jpg")

    img1size = img1.size
    img2size = img2.size

    img1 = img1.resize((int(img1size[0] * 0.8), int(img1size[1] * 0.8)))
    img2 = img2.resize((int(img2size[0] * 1.2), int(img2size[1] * 1.2)))

    total_width = max(img1.size[0], img2.size[0])
    total_height = img1.size[1] + img2.size[1]
    new_im = Image.new('RGB', (total_width, total_height), (255, 255, 255))

    x_position1 = int((total_width - img1.size[0]) / 2)
    new_im.paste(img1, (x_position1, 0))

    x_position2 = int((total_width - img2.size[0]) / 2)
    new_im.paste(img2, (x_position2, img1.size[1]))

    draw = ImageDraw.Draw(new_im)
    line_y = img1.size[1]
    draw.line([(0, line_y), (new_im.width, line_y)], fill=(0, 0, 0), width=3)

    new_im.save(f"memesDone/{converted_img}")

    random_number = random.randint(1, 100)
    counter3 += 1

for i in range(25):
    ConvertImageTo1(converted_img=f"memes{counter3}.jpg")


counter2 = 1


# Add images to video

def ImgAdd(video, image, position=("center", "center")):
    global counter2

    video = VideoFileClip(video)

    image = ImageClip(image)

    image = image.resize(height=video.h - 1000)

    duration = video.duration
    image = image.set_duration(duration).set_position(position).set_fps(video.fps)

    final_video = CompositeVideoClip([video, image])

    final_video.write_videofile(f"videos/output{counter2}.mp4", codec='libx264', fps=video.fps)
    counter2 += 1

for i in range(25):
    ImgAdd(video="VideoTemplate.mp4", image=f"memesDone/memes{counter2}.jpg")



pause()

# Upload Videos

CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

counter4 = 1

def upload_video(videoname):
    global counter4

    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_UPLOAD_SCOPE)
    storage = Storage("youtube-oauth2.json")
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)
    
    title="Funnyest Internet MEMEs of all Time 😂😂"
    description=title

    keywords = "funny, memes, shorts"

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "keywords": keywords,
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": "public",
        }
    }
    
    file_path="videos"

    try:
        media_body = MediaFileUpload(videoname, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media_body)
        print("Uploading video...")
        response = request.execute()
        print(f"Video uploaded! Video ID: {response['id']}")
    except (HttpError, NameError, FileNotFoundError):
        pass

    counter4 += 1

for i in range(25):
    upload_video(videoname=f"videos/output{counter4}.mp4")