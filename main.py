import requests
import os
import base64
import random
import time
import io
import json
from openai import OpenAI

from flask import Flask
from google.cloud import storage
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

app = Flask(__name__)

# Replace with your own page access token and verify token
PAGE_ACCESS_TOKEN = os.environ.get('INSTA_PAGE_ACCESS_TOKEN', '')
VERIFY_TOKEN = os.environ.get('INSTA_PAGE_VERIFY_TOKEN', '')
BUSINESS_ACCOUNT_ID = os.environ.get('INSTA_BUSINESS_ACCOUNT_ID', '')
STABILITY_KEY = os.environ.get('STABILITY_KEY', '')
client = OpenAI(api_key=os.environ.get('OPENAI_TOKEN', ''))

AI_ENGINE = 'gpt-3.5-turbo-1106'

topic = [
   "city",
   "world heritage",
   "sightseeing place",
   "airport",
   "train station",
   "sea port",
   "bridge",
   "zoo",
   "aquarium",
   "theme park"
]

place = [
    "North America",
    "South America",
    "Asia",
    "Europe",
    "Africa",
    "Oceania"
]

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

@app.route('/stability_post_insta', methods=['GET'])
def stability_post_insta():

    # pick topic and place randomly
    picked_topic = random.choice(topic)
    picked_place = random.choice(place)
    picked_pattern = random.choice(pattern)

    # make openai parameter
    input = []
    text = f'pick one {picked_topic} in {picked_place} countries.'
    # text = 'pick one place all over the world'
    new_message = {"role":"user", "content":text}
    input.append(new_message)

    # send message to openai api
    result = client.chat.completions.create(model=AI_ENGINE, messages=input)    
    ai_response = result.choices[0].message.content
    print(ai_response)

    # for genarating images prompt
    my_prompt = f"{ai_response}, {picked_pattern}"
    print(my_prompt)

    # generate image by stability
    stability_api = client.StabilityInference(key=STABILITY_KEY, verbose=True)
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

    caption = f"This is an image of {ai_response} created by image generation Stable Diffusion API #stablediffusion #texttoimage #api"

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

    print('Image uploaded and published successfully!')

    if os.path.exists(image_path): # check if the file exists
        os.remove(image_path) # delete the file
        print(f"{image_path} has been deleted.")
    else:
        print(f"{image_path} does not exist.")

    return "ok", 200

@app.route('/openai_post_insta', methods=['GET'])
def openai_post_insta():

    # pick topic and place randomly
    picked_topic = random.choice(topic)
    picked_place = random.choice(place)
    picked_pattern = random.choice(pattern)

    # make openai parameter
    input = []
    text = f'pick one {picked_topic} in {picked_place} countries.'
    # text = 'pick one place all over the world'
    new_message = {"role":"user", "content":text}
    input.append(new_message)

    # send message to openai api
    result = client.chat.completions.create(model=AI_ENGINE, messages=input)    
    ai_response = result.choices[0].message.content
    print(ai_response)

    # for genarating images prompt
    my_prompt = f"{ai_response}, {picked_pattern}"
    print(my_prompt)

    # generate image by openai
    response = client.images.generate(
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

    # vision api making image details
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"What are in this image? Describe it good for sns post. The image title tells that {ai_response}",
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

    caption = f"{ai_response} #chatgpt #openai #api #dalle3 #texttoimage"

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

    if os.path.exists(image_path): # check if the file exists
        os.remove(image_path) # delete the file
        print(f"{image_path} has been deleted.")
    else:
        print(f"{image_path} does not exist.")

    return "ok", 200

@app.route('/remove_bucket_imgs', methods=['GET'])
def remove_bucket_imgs():
    # Delete all files from a Google Cloud Storage bucket.
    delete_bucket_files("ai-bot-app-insta")
    return "ok", 200

# Delete all files from a Google Cloud Storage bucket.
def delete_bucket_files(bucket_name):
    # Create a Cloud Storage client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # List all blobs in the bucket
    blobs = bucket.list_blobs()

    # Delete each blob in the bucket
    for blob in blobs:
        blob.delete()
        print(f"Deleted {blob.name}.")

    print(f"All files in {bucket_name} have been deleted.")

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

if __name__ == '__main__':
    app.run(debug=True)
