# AI Social Media Bot

A Python-based bot that uses Generative AI to create and post content to Instagram and Threads. It integrates with Stability AI, DALL-E 3, and Google Imagen for image generation and uses Google Gemini for intelligent caption creation.

## 🚀 Core Features

- **Multi-Provider Image Generation**: Creates images using Stability AI, DALL-E 3, and Google Imagen.
- **Automated Posting**: Publishes generated content to Instagram (feed and stories) and Threads.
- **Intelligent Captioning**: Leverages the Gemini vision model to generate relevant captions for your images.
- **Advanced Prompt Engineering**: Enhances basic prompts with additional styles, lighting, and composition details to create more dynamic images.
- **Cloud Storage Integration**: Automatically uploads and serves images from Google Cloud Storage.
- **A/B Testing Framework**: Includes endpoints to test and compare different prompt strategies.

## 🔧 Setup and Configuration

### 1. Prerequisites
- Python 3.8+
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and authenticated.
- A Google Cloud project with the Cloud Storage API enabled.

### 2. Installation
Clone the repository and install the required Python packages:
```bash
git clone https://github.com/your-username/ai_bot_app_insta.git
cd ai_bot_app_insta
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the project root or set the following environment variables.

#### **API Credentials**
```bash
# Instagram & Threads Configuration
INSTA_PAGE_ACCESS_TOKEN="your_instagram_page_access_token"
INSTA_PAGE_VERIFY_TOKEN="your_webhook_verification_token"
INSTA_BUSINESS_ACCOUNT_ID="your_instagram_business_account_id"
THREADS_API_TOKEN="your_threads_api_token"
THREADS_USER_ID="your_threads_user_id"

# AI Provider Keys
OPENAI_TOKEN="your_openai_api_key"
STABILITY_KEY="your_stability_ai_key"
GEMINI_API_KEY="your_google_gemini_key"
```

#### **Prompt Tuning (Optional)**
```bash
# Enable/disable advanced prompt features
ENABLE_ENHANCED_PROMPTS=true
ENABLE_NEGATIVE_PROMPTS=true
PROMPT_COMPLEXITY_LEVEL=2  # 1=simple, 2=enhanced, 3=complex
```

## ⚙️ Usage

### Local Development
To run the Flask server locally for development and testing:
```bash
flask run
```
The application will be available at `http://127.0.0.1:5000`.

### API Endpoints

#### **Content Generation**
Trigger a post using one of the following endpoints. Each endpoint generates an image with a different AI provider, creates a caption, and posts to Instagram and Threads.

- **Stability AI**: `GET /stability_post_insta`
- **DALL-E 3**: `GET /openai_post_insta`
- **Google Imagen**: `GET /imagen_post_insta`

**Example:**
```bash
curl http://127.0.0.1:5000/stability_post_insta
```

#### **Testing & Analytics**
- `GET /test_prompt_strategies`: A/B test different prompt generation strategies.
- `GET /prompt_performance`: View performance statistics for prompts.
- `POST /reset_prompt_performance`: Reset the performance tracker.

## 🚀 Deployment

This application is designed to be deployed as a serverless container, for example, using Google Cloud Run.

To deploy to Google Cloud Run:
```sh
gcloud run deploy ai-bot-app-insta --source . --allow-unauthenticated --region=asia-northeast1 --project=yahayuta
```

## 📄 License

This project is open source. Feel free to modify and adapt it for your needs.
