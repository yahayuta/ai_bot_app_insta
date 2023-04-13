import requests
import os
import openai
import base64
import random

from flask import Flask
from google.cloud import storage

app = Flask(__name__)

# Replace with your own page access token and verify token
PAGE_ACCESS_TOKEN = os.environ.get('INSTA_PAGE_ACCESS_TOKEN', '')
VERIFY_TOKEN = os.environ.get('INSTA_PAGE_VERIFY_TOKEN', '')
BUSINESS_ACCOUNT_ID = os.environ.get('INSTA_BUSINESS_ACCOUNT_ID', '')
openai.api_key = os.environ.get('OPENAI_TOKEN', '')

AI_ENGINE = 'gpt-3.5-turbo'

topic = [
   "musician or group or band",
   "movie",
   "drama",
   "place"
]

@app.route('/openai_post_insta', methods=['GET'])
def openai_post_insta():

    # pick topic randomly
    picked_topic = random.choice(topic)

    # make openai parameter
    input = []
    text = f'pick one famous {picked_topic} all over the world.'
    new_message = {"role":"user", "content":text}
    input.append(new_message)

    # send message to openai api
    result = openai.ChatCompletion.create(model=AI_ENGINE, messages=input)    
    ai_response = result.choices[0].message.content
    print(ai_response)

    response = openai.Image.create(
        prompt=ai_response,
        n=1,
        size="512x512",
        response_format="b64_json",
    )

    image_path = f"image_{BUSINESS_ACCOUNT_ID}.png"
    for data, n in zip(response["data"], range(1)):
        img_data = base64.b64decode(data["b64_json"])
        with open(image_path, "wb") as f:
            f.write(img_data)

    image_url = upload_to_bucket("image_path", image_path, "ai-bot-app-insta")

    # Upload the image to Facebook
    url = f"https://graph.facebook.com/{BUSINESS_ACCOUNT_ID}/media"
    params = {'access_token': PAGE_ACCESS_TOKEN, 'image_url':image_url, 'caption':ai_response}
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

if __name__ == '__main__':
    app.run(debug=True)