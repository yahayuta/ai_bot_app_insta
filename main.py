import requests
import os
import random
import time
import io
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

from openai import OpenAI
from flask import Flask
from google.cloud import storage
from PIL import Image
from stability_sdk import client

app = Flask(__name__)

# Replace with your own page access token and verify token
PAGE_ACCESS_TOKEN = os.environ.get('INSTA_PAGE_ACCESS_TOKEN', '')
VERIFY_TOKEN = os.environ.get('INSTA_PAGE_VERIFY_TOKEN', '')
BUSINESS_ACCOUNT_ID = os.environ.get('INSTA_BUSINESS_ACCOUNT_ID', '')
STABILITY_KEY = os.environ.get('STABILITY_KEY', '')
openai = OpenAI(api_key=os.environ.get('OPENAI_TOKEN', ''))

pattern = [
    "illustration",
    "stencil art",
    "crayon",
    "crayon art",
    "chalk",
    "chalk art",
    "etching",
    "oil paintings",
    "ballpoint pen",
    "ballpoint pen art",
    "colored pencil",
    "watercolor",
    "Chinese watercolor",
    "pastels",
    "woodcut",
    "charcoal",
    "line drawing",
    "screen print",
    "photocollage",
    "storybook illustration",
    "newspaper cartoon",
    "vintage illustration from 1960s",
    "vintage illustration from 1980s",
    "anime style",
    "anime style, official art",
    "manga style",
    "Studio Ghibli style",
    "kawaii",
    "pixel art",
    "screenshot from SNES game",
    "vector illustration",
    "sticker art",
    "3D illustration",
    "cute 3D illustration in the style of Pixar",
    "Octane Render",
    "digital art",
    "2.5D",
    "isometric art",
    "ceramic art",
    "geometric art",
    "surrealism",
    "Dadaism",
    "metaphysical painting",
    "orphism",
    "cubism",
    "suprematism",
    "De Stijl",
    "futurism",
    "expressionism",
    "realism",
    "impressionism",
    "Art Nouveau",
    "baroque painting",
    "rococo painting",
    "mannerism painting",
    "bauhaus painting",
    "ancient Egyptian papyrus",
    "ancient Roman mosaic",
    "ukiyo-e",
    "painted in the style of Vincent van Gogh",
    "painted in the style of Alphonse Mucha",
    "painted in the style of Sophie Anderson",
    "painting by Vincent van Gogh",
    "painting by Alphonse Mucha",
    "painting by Sophie Anderson",  
]

cartoons = [
    "Naruto",
    "Dragon Ball Z",
    "One Piece",
    "Sailor Moon",
    "Pokémon",
    "Attack on Titan",
    "My Hero Academia",
    "Death Note",
    "Fullmetal Alchemist",
    "Bleach",
    "Neon Genesis Evangelion",
    "Cowboy Bebop",
    "Spirited Away",
    "Demon Slayer: Kimetsu no Yaiba",
    "Tokyo Ghoul",
    "One Punch Man",
    "Hunter x Hunter",
    "Fairy Tail",
    "JoJo's Bizarre Adventure",
    "Yu Yu Hakusho",
    "Mob Psycho 100",
    "Akira",
    "Your Name",
    "Sword Art Online",
    "Naruto Shippuden",
    "Death Parade",
    "Ghost in the Shell",
    "Ranma ½",
    "Black Clover",
    "Digimon",
    "Initial D",
    "Gurren Lagann",
    "Inuyasha",
    "Cardcaptor Sakura",
    "Gintama",
    "The Promised Neverland",
    "Parasyte -the maxim-",
    "Code Geass",
    "Trigun",
    "Rurouni Kenshin",
    "Kill la Kill",
    "Wolf's Rain",
    "Fate/stay night",
    "Berserk",
    "Tokyo Mew Mew",
    "Slam Dunk",
    "Detective Conan (Case Closed)",
    "Doraemon",
    "Astro Boy",
    "Kimba the White Lion (Jungle Emperor)",
    "Speed Racer (Mach GoGoGo)",
    "Heidi, Girl of the Alps",
    "Princess Knight (Ribon no Kishi)",
    "Sazae-san",
    "Lupin III",
    "Cyborg 009",
    "Gatchaman (Science Ninja Team Gatchaman)",
    "Dragon Ball",
    "Mazinger Z",
    "Candy Candy",
    "Getter Robo",
    "Space Battleship Yamato (Star Blazers)",
    "Tiger Mask",
    "GeGeGe no Kitaro",
    "Jungle Emperor Leo (Leo the Lion)",
    "Obake no Q-tarō",
    "Akage no Anne (Anne of Green Gables)",
    "Princess Sarah (A Little Princess Sara)",
    "Galaxy Express 999",
    "The Rose of Versailles (Versailles no Bara)",
    "Devilman",
    "Future Boy Conan",
    "Tetsujin 28-go (Gigantor)",
    "Urusei Yatsura (Lum Invader)",
    "The Adventures of Hutch the Honeybee",
    "Dokonjō Gaeru (The Gutsy Frog)",
    "Captain Tsubasa",
    "Maison Ikkoku",
    "Nausicaä of the Valley of the Wind",
    "Kinnikuman (Muscle Man)",
    "Science Ninja Team Gatchaman",
    "Lupin III: Part II",
    "Ganbare!! Tabuchi-kun!!",
    "Sally the Witch (Mahōtsukai Sarī)",
    "Yatterman",
    "Himitsu no Akko-chan (Secret Akko-chan)",
    "The Snow Queen",
    "Panda! Go, Panda!",
    "Space Pirate Captain Harlock",
    "Dokaben",
    "Tensai Bakabon",
    "Combattler V",
    "Casshan",
    "Cutie Honey",
    "Magical Princess Minky Momo",
    "Gekisou! Rubenkaiser",
    "Hana no Ko Lunlun"
]

@app.route('/stability_post_insta', methods=['GET'])
def stability_post_insta():

    # pick cartoon and pattern
    picked_cartoon = random.choice(cartoons)
    picked_pattern = random.choice(pattern)

    # for genarating images prompt
    my_prompt = f"{picked_cartoon}, {picked_pattern}"
    print(my_prompt)

    # generate image by stability
    stability_api = client.StabilityInference(
        key=STABILITY_KEY, 
        verbose=True,
        engine="stable-diffusion-xl-1024-v1-0",)
    answers = stability_api.generate(prompt=my_prompt)

    # save image as file
    image_path = f"/tmp/image_{BUSINESS_ACCOUNT_ID}.png"
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                print("NSFW")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                img.save(image_path)

    current_time = int(time.time())
    current_time_string = str(current_time)

    # Uploads a file to the Google Cloud Storage bucket
    image_url = upload_to_bucket(current_time_string, image_path, "ai-bot-app-insta")
    print(image_url)

    ai_response = exec_openai_vision(image_url, my_prompt)
    print(ai_response)

    caption = f"{ai_response} #api #stabilityai #stablediffusion #texttoimage"

    exec_instagram_post(image_url, caption)

    if os.path.exists(image_path): # check if the file exists
        os.remove(image_path) # delete the file
        print(f"{image_path} has been deleted.")
    else:
        print(f"{image_path} does not exist.")

    return "ok", 200

@app.route('/openai_post_insta', methods=['GET'])
def openai_post_insta():

    # pick cartoon and pattern
    picked_cartoon = random.choice(cartoons)
    picked_pattern = random.choice(pattern)

    # for genarating images prompt
    my_prompt = f"{picked_cartoon}, {picked_pattern}"
    print(my_prompt)

    # generate image by openai
    response = openai.images.generate(
        model="dall-e-3",
        prompt=my_prompt,
        n=1,
        size="1024x1024",
    )

    print(response)

    url = response.data[0].url

    response = requests.get(url)

    # save image as file
    image_path = f"/tmp/image_{BUSINESS_ACCOUNT_ID}.png"

    with open(image_path, 'wb') as file:
        file.write(response.content)

    current_time = int(time.time())
    current_time_string = str(current_time)

    # Uploads a file to the Google Cloud Storage bucket
    image_url = upload_to_bucket(current_time_string, image_path, "ai-bot-app-insta")
    print(image_url)

    ai_response = exec_openai_vision(image_url, my_prompt)
    print(ai_response)

    caption = f"{ai_response} #chatgpt #openai #api #dalle3 #texttoimage"
    
    exec_instagram_post(image_url, caption)

    if os.path.exists(image_path): # check if the file exists
        os.remove(image_path) # delete the file
        print(f"{image_path} has been deleted.")
    else:
        print(f"{image_path} does not exist.")

    return "ok", 200

#  Uploads a file to the Google Cloud Storage bucket
def upload_to_bucket(blob_name, file_path, bucket_name):
    # Create a Cloud Storage client
    storage_client = storage.Client()

    # Get the bucket that the file will be uploaded to
    bucket = storage_client.bucket(bucket_name)

    # Create a new blob and upload the file's content
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)

    # Make the blob publicly viewable
    blob.make_public()

    # Return the public URL of the uploaded file
    return blob.public_url

# vision api making image details
def exec_openai_vision(image_url, my_prompt):
    response = openai.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"What are in this image? Describe it good for sns post. The image title tells that {my_prompt}",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                    },
                },
            ],
            }
        ],
        max_tokens=1000,
    )

    ai_response = response.choices[0].message.content
    print(ai_response)
    return ai_response

# post image and text to instagram
def exec_instagram_post(image_url, caption):

    # Upload the image to Facebook
    url = f"https://graph.facebook.com/{BUSINESS_ACCOUNT_ID}/media"
    params = {'access_token': PAGE_ACCESS_TOKEN, 'image_url':image_url, 'caption':caption}
    response = requests.post(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to upload image: {response.text}")
    media_id = response.json()['id']

    # Publish the photo to Instagram
    url = f"https://graph.facebook.com/{BUSINESS_ACCOUNT_ID}/media_publish"
    params = {'access_token': PAGE_ACCESS_TOKEN, 'creation_id': media_id}
    response = requests.post(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to publish photo: {response.text}")

    # Upload the image to Facebook as story
    url = f"https://graph.facebook.com/{BUSINESS_ACCOUNT_ID}/media"
    params = {'access_token': PAGE_ACCESS_TOKEN, 'image_url':image_url, 'media_type':'STORIES'}
    response = requests.post(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to upload image: {response.text}")
    media_id = response.json()['id']

    # Publish the photo to Instagram as story
    url = f"https://graph.facebook.com/{BUSINESS_ACCOUNT_ID}/media_publish"
    params = {'access_token': PAGE_ACCESS_TOKEN, 'creation_id': media_id}
    response = requests.post(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to publish photo: {response.text}")
    
    print('Image uploaded and published successfully!')

if __name__ == '__main__':
    app.run(debug=True)
