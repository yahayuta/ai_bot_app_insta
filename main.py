# --- Standard Library Imports ---
import io
import os  # For environment variables and file operations
import random  # For random selection of topics, patterns, etc.
import time  # For timestamping image files
import base64  # For encoding images for API requests
from io import BytesIO  # For in-memory image operations

# --- Third-Party Imports ---
import requests  # type: ignore # For HTTP requests to APIs
from flask import Flask  # type: ignore # For web server and API endpoints
from PIL import Image  # type: ignore # For image processing

# Stability AI SDK (for image generation)
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation  # type: ignore # For artifact types
from stability_sdk import client  # type: ignore # For Stability API client

# OpenAI (for text and image generation)
from openai import OpenAI  # type: ignore # For OpenAI API client

# Google Cloud & Gemini (for storage and vision models)
from google.cloud import storage  # For Google Cloud Storage
from google import genai  # For Gemini API
from google.genai import types  # type: ignore # For Gemini API types

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Environment Variables ---
# These should be set in your environment or .env file for security and flexibility.
PAGE_ACCESS_TOKEN = os.environ.get('INSTA_PAGE_ACCESS_TOKEN', '')  # Instagram page access token
VERIFY_TOKEN = os.environ.get('INSTA_PAGE_VERIFY_TOKEN', '')      # Webhook verification token
BUSINESS_ACCOUNT_ID = os.environ.get('INSTA_BUSINESS_ACCOUNT_ID', '')  # Instagram business account ID
STABILITY_KEY = os.environ.get('STABILITY_KEY', '')              # Stability AI API key
openai = OpenAI(api_key=os.environ.get('OPENAI_TOKEN', ''))       # OpenAI API client
OPENAI_MODEL = 'gpt-4o-mini'                                     # OpenAI model to use
THREADS_API_TOKEN = os.environ.get('THREADS_API_TOKEN', '')      # Threads API token
THREADS_USER_ID = os.environ.get('THREADS_USER_ID', '')          # Threads user ID

# --- Content Categories ---
# These lists are used to randomly select topics, places, and art styles for content generation.
topic = [
    "musician or group or band", "movie", "drama", "place", "politician",
    "athlete", "comedian", "actor", "actress", "city", "book",
    "historical figure", "animal", "food", "sport", "company", "brand",
    "technology", "scientific discovery", "natural phenomenon",
    "mythical creature", "video game character", "cartoon character",
    "inventor", "religious figure", "festival or event", "fashion designer",
    "Youtuber or influencer", "fictional character from novel", "myth or legend",
    "philosopher", "scientist", "TV host", "journalist", "robot or AI",
    "superhero", "villain", "podcast", "startup founder", "military leader"
]

place = [
    "North America", "South America", "Asia", "Europe", "Africa", "Oceania",
    "Middle East", "Antarctica", "Central America", "Caribbean", "Arctic Circle",
    "Amazon Rainforest", "Himalayan region", "Balkan Peninsula",
    "Scandinavia", "Southeast Asia"
]

pattern = [
    "illustration", "stencil art", "crayon", "crayon art", "chalk", "chalk art",
    "etching", "oil paintings", "ballpoint pen", "ballpoint pen art",
    "colored pencil", "watercolor", "Chinese watercolor", "pastels", "woodcut",
    "charcoal", "line drawing", "screen print", "photocollage",
    "storybook illustration", "newspaper cartoon", "vintage illustration from 1960s",
    "vintage illustration from 1980s", "anime style", "anime style, official art",
    "manga style", "Studio Ghibli style", "kawaii", "pixel art",
    "screenshot from SNES game", "vector illustration", "sticker art",
    "3D illustration", "cute 3D illustration in the style of Pixar",
    "Octane Render", "digital art", "2.5D", "isometric art", "ceramic art",
    "geometric art", "surrealism", "Dadaism", "metaphysical painting", "orphism",
    "cubism", "suprematism", "De Stijl", "futurism", "expressionism", "realism",
    "impressionism", "Art Nouveau", "baroque painting", "rococo painting",
    "mannerism painting", "bauhaus painting", "ancient Egyptian papyrus",
    "ancient Roman mosaic", "ukiyo-e", "painted in the style of Vincent van Gogh",
    "painted in the style of Alphonse Mucha", "painted in the style of Sophie Anderson",
    "painting by Vincent van Gogh", "painting by Alphonse Mucha", "painting by Sophie Anderson",
    "linocut", "airbrush art", "graffiti style", "pop art",
    "collage with fabric textures", "low poly 3D art", "papercut art",
    "gouache painting", "cyberpunk style digital art", "steampunk illustration",
    "hyperrealistic digital painting", "AI-generated art", "mixed media",
    "glitch art", "punk zine collage", "flat design", "grunge poster style",
    "Y2K style graphics", "generative fractal art", "VR sculpture screenshot"
]

cartoons = [
    "Naruto", "Dragon Ball Z", "One Piece", "Sailor Moon", "Pokémon", "Attack on Titan",
    "My Hero Academia", "Death Note", "Fullmetal Alchemist", "Bleach",
    "Neon Genesis Evangelion", "Cowboy Bebop", "Spirited Away",
    "Demon Slayer: Kimetsu no Yaiba", "Tokyo Ghoul", "One Punch Man",
    "Hunter x Hunter", "Fairy Tail", "JoJo's Bizarre Adventure", "Yu Yu Hakusho",
    "Mob Psycho 100", "Akira", "Your Name", "Sword Art Online", "Naruto Shippuden",
    "Death Parade", "Ghost in the Shell", "Ranma ½", "Black Clover", "Digimon",
    "Initial D", "Gurren Lagann", "Inuyasha", "Cardcaptor Sakura", "Gintama",
    "The Promised Neverland", "Parasyte -the maxim-", "Code Geass", "Trigun",
    "Rurouni Kenshin", "Kill la Kill", "Wolf's Rain", "Fate/stay night", "Berserk",
    "Tokyo Mew Mew", "Slam Dunk", "Detective Conan (Case Closed)", "Doraemon",
    "Astro Boy", "Kimba the White Lion (Jungle Emperor)", "Speed Racer (Mach GoGoGo)",
    "Heidi, Girl of the Alps", "Princess Knight (Ribon no Kishi)", "Sazae-san",
    "Lupin III", "Cyborg 009", "Gatchaman (Science Ninja Team Gatchaman)",
    "Dragon Ball", "Mazinger Z", "Candy Candy", "Getter Robo",
    "Space Battleship Yamato (Star Blazers)", "Tiger Mask", "GeGeGe no Kitaro",
    "Jungle Emperor Leo (Leo the Lion)", "Obake no Q-tarō", "Akage no Anne (Anne of Green Gables)",
    "Princess Sarah (A Little Princess Sara)", "Galaxy Express 999",
    "The Rose of Versailles (Versailles no Bara)", "Devilman", "Future Boy Conan",
    "Tetsujin 28-go (Gigantor)", "Urusei Yatsura (Lum Invader)",
    "The Adventures of Hutch the Honeybee", "Dokonjō Gaeru (The Gutsy Frog)",
    "Captain Tsubasa", "Maison Ikkoku", "Nausicaä of the Valley of the Wind",
    "Kinnikuman (Muscle Man)", "Science Ninja Team Gatchaman", "Lupin III: Part II",
    "Ganbare!! Tabuchi-kun!!", "Sally the Witch (Mahōtsukai Sarī)", "Yatterman",
    "Himitsu no Akko-chan (Secret Akko-chan)", "The Snow Queen",
    "Panda! Go, Panda!", "Space Pirate Captain Harlock", "Dokaben",
    "Tensai Bakabon", "Combattler V", "Casshan", "Cutie Honey",
    "Magical Princess Minky Momo", "Gekisou! Rubenkaiser", "Hana no Ko Lunlun",
    "Chainsaw Man", "Jujutsu Kaisen", "Blue Lock", "Oshi no Ko",
    "Frieren: Beyond Journey’s End", "Spy x Family", "The Dangers in My Heart",
    "Dr. Stone", "Vinland Saga", "Summertime Rendering", "Horimiya",
    "SK8 the Infinity", "Ranking of Kings", "To Your Eternity",
    "Mushoku Tensei: Jobless Reincarnation", "Re:Zero − Starting Life in Another World",
    "Erased (Boku dake ga Inai Machi)", "Kaguya-sama: Love is War",
    "Made in Abyss", "86 (Eighty-Six)"
]

# --- Flask Endpoints ---

@app.route('/stability_post_insta', methods=['GET'])
def stability_post_insta():
    """
    Generate an image using Stability AI based on a random cartoon and art pattern,
    upload it to Google Cloud Storage, generate a caption using Gemini vision model,
    and post to Instagram and Threads.
    """
    # Pick a random cartoon and art pattern for the image generation
    picked_cartoon = random.choice(cartoons)
    picked_pattern = random.choice(pattern)

    # for generating image prompt
    my_prompt = f"{picked_cartoon}, {picked_pattern}"
    print(my_prompt)

    # generate image by stability
    stability_api = client.StabilityInference(
        key=STABILITY_KEY, 
        verbose=True,
        engine="stable-diffusion-xl-1024-v1-0",)
    answers = stability_api.generate(prompt=my_prompt)

    current_time = int(time.time())
    current_time_string = str(current_time)

    # save image as file
    image_path = f"/tmp/image_{BUSINESS_ACCOUNT_ID}_{current_time_string}.png"
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                print("NSFW")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                img.save(image_path)

    # Uploads a file to the Google Cloud Storage bucket
    image_url = upload_to_bucket(current_time_string, image_path, "ai-bot-app-insta")
    print(image_url)

    # Generate caption using vision model
    ai_response = gemini_chat_with_image(image_path, get_chat_with_image_template(my_prompt))
    print(ai_response)

    caption = f"{ai_response} #api #stabilityai #stablediffusion #texttoimage"

    exec_instagram_post(image_url, caption)
    exec_threads_post(image_url, caption)

    remove_img_file(image_path)

    return "ok", 200

@app.route('/openai_post_insta', methods=['GET'])
def openai_post_insta():
    """
    Generate a topic and place, use OpenAI to create a short description,
    generate an image with DALL-E, upload to Google Cloud Storage,
    generate a caption with Gemini, and post to Instagram and Threads.
    """
    # pick topic randomly
    picked_topic = random.choice(topic)
    picked_place = random.choice(place)

    # make openai parameter
    input = []
    text = f'pick one {picked_topic} in {picked_place} countries then talk about it very shortly'
    new_message = {"role":"user", "content":text}
    input.append(new_message)

    # generate text by openai
    print(f"OpenAI input: {input}")
    result = openai.chat.completions.create(model=OPENAI_MODEL, messages=input)
    ai_response = result.choices[0].message.content
    
    # for genarating images prompt
    picked_pattern = random.choice(pattern)
    my_prompt = f"{ai_response}, {picked_pattern}"
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

    current_time = int(time.time())
    current_time_string = str(current_time)

    # save image as file
    image_path = f"/tmp/image_{BUSINESS_ACCOUNT_ID}_{current_time_string}.png"
    with open(image_path, 'wb') as file:
        file.write(response.content)

    # Uploads a file to the Google Cloud Storage bucket
    image_url = upload_to_bucket(current_time_string, image_path, "ai-bot-app-insta")
    print(image_url)

    # Generate caption using vision model
    ai_response = gemini_chat_with_image(image_path, get_chat_with_image_template(my_prompt))
    print(ai_response)

    caption = f"{ai_response} #chatgpt #openai #api #dalle3 #texttoimage"
    
    exec_instagram_post(image_url, caption)
    exec_threads_post(image_url, caption)

    remove_img_file(image_path)

    return "ok", 200

@app.route('/imagen_post_insta', methods=['GET'])
def imagen_post_insta():
    """
    Generate an image using Google Imagen, upload to Google Cloud Storage,
    generate a caption with Gemini, and post to Instagram and Threads.
    """
    # pick cartoon and pattern
    picked_cartoon = random.choice(cartoons)
    picked_pattern = random.choice(pattern)

    # for generating image prompt
    my_prompt = f"{picked_cartoon}, {picked_pattern}"
    print(my_prompt)

    # Generate image using Imagen (Google)
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    result = client.models.generate_images(
        model="models/imagen-3.0-generate-002",
        prompt=my_prompt,
        config=dict(
            number_of_images=1,
            output_mime_type="image/jpeg",
            person_generation="ALLOW_ADULT",
            aspect_ratio="1:1",
        ),
    )

    if not result.generated_images:
        print("No images generated.")
        return "No image generated", 500

    image_data = result.generated_images[0].image.image_bytes
    img = Image.open(BytesIO(image_data))

    current_time = int(time.time())
    current_time_string = str(current_time)

    # Save image as file
    image_path = f"/tmp/image_{BUSINESS_ACCOUNT_ID}_{current_time_string}.jpg"
    img.save(image_path)

    # Upload image to Google Cloud Storage
    image_url = upload_to_bucket(current_time_string, image_path, "ai-bot-app-insta")
    print(image_url)

    # Generate caption using vision model
    ai_response = gemini_chat_with_image(image_path, get_chat_with_image_template(my_prompt))
    print(ai_response)

    caption = f"{ai_response} #api #google #imagen #texttoimage"

    # Post to Instagram and Threads
    exec_instagram_post(image_url, caption)
    exec_threads_post(image_url, caption)

    # Clean up temporary image file
    remove_img_file(image_path)

    return "ok", 200

# --- Utility Functions ---

def upload_to_bucket(blob_name, file_path, bucket_name):
    """
    Upload a file to Google Cloud Storage and return its public URL.
    """
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

def exec_openai_vision(image_url, my_prompt):
    """
    Use OpenAI's vision model to generate a description for an image.
    """
    response = openai.chat.completions.create(
        model=OPENAI_MODEL,
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

def gemini_chat_with_image(image_path, prompt_text):
    """
    Use Gemini API to generate a caption for an image given a prompt.
    """
    try:
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()
        encoded_image = base64.b64encode(image_bytes)

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(mime_type="image/jpeg", data=base64.b64decode(encoded_image)),
                    types.Part.from_text(text=prompt_text)
                ],
            )
        ]

        generate_content_config = types.GenerateContentConfig(response_mime_type="text/plain")

        genai_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        # Generate content with image and text
        response = ""
        for chunk in genai_client.models.generate_content_stream(
            model="gemini-2.5-flash-preview-05-20",
            contents=contents,
            config=generate_content_config,
        ):
            response += chunk.text or ""
        return response

    except Exception as e:
        print(f"Error during image + text Gemini request: {e}")
        return f"Error: {e}"

def exec_instagram_post(image_url, caption):
    """
    Post an image and caption to Instagram (feed and story).
    """
    # Upload the image to Facebook
    url = f"https://graph.instagram.com/v22.0/{BUSINESS_ACCOUNT_ID}/media"
    params = {'access_token': PAGE_ACCESS_TOKEN, 'image_url':image_url, 'caption':caption}
    response = requests.post(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to upload image: {response.text}")
    media_id = response.json()['id']

    # Publish the photo to Instagram
    url = f"https://graph.instagram.com/v22.0/{BUSINESS_ACCOUNT_ID}/media_publish"
    params = {'access_token': PAGE_ACCESS_TOKEN, 'creation_id': media_id}
    response = requests.post(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to publish photo: {response.text}")

    # Upload the image to Facebook as story
    url = f"https://graph.instagram.com/v22.0/{BUSINESS_ACCOUNT_ID}/media"
    params = {'access_token': PAGE_ACCESS_TOKEN, 'image_url':image_url, 'media_type':'STORIES'}
    response = requests.post(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to upload image: {response.text}")
    media_id = response.json()['id']

    # Publish the photo to Instagram as story
    url = f"https://graph.instagram.com/v22.0/{BUSINESS_ACCOUNT_ID}/media_publish"
    params = {'access_token': PAGE_ACCESS_TOKEN, 'creation_id': media_id}
    response = requests.post(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to publish photo: {response.text}")
    
    print('instagram Image uploaded and published successfully!')

def exec_threads_post(image_url, text = ''):
    """
    Post an image and text to Threads.
    """
    # Truncate text to 500 characters as required by Threads API
    if len(text) > 500:
        text = text[:500]

    # Upload the image to Facebook
    url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads"
    params = {'access_token': THREADS_API_TOKEN, 'media_type':'IMAGE', 'image_url':image_url, 'text':text}
    response = requests.post(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to upload image: {response.text}")
    media_id = response.json()['id']

    # Publish the photo to Instagram
    url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish"
    params = {'access_token': THREADS_API_TOKEN, 'creation_id': media_id}
    response = requests.post(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to publish photo: {response.text}")
    
    print('threads Image uploaded and published successfully!')

def remove_img_file(image_path):
    """
    Remove a temporary image file from the filesystem.
    """
    if os.path.exists(image_path): # check if the file exists
        os.remove(image_path) # delete the file
        print(f"{image_path} has been deleted.")
    else:
        print(f"{image_path} does not exist.")
        
def get_chat_with_image_template(prompt):
    """
    Return a template prompt for describing an image for social media.
    """
    return f"What are in this image? Describe it good for sns post. Return only text of description. The image title tells that {prompt}."

if __name__ == '__main__':
    # Run the Flask app in debug mode for local development
    app.run(debug=True)
