# ai_bot_app_insta

This project is a Python-based Instagram bot app that utilizes the OpenAI API (ChatGPT) and can be deployed to Google Cloud Run. It demonstrates how to automate Instagram content creation and posting using AI-generated text and images.

## Features
- Communicates with the OpenAI API (ChatGPT) to generate captions or content.
- Example endpoints for generating and posting content to Instagram.
- Designed for deployment on Google Cloud Run.
- Highly configurable via environment variables.

## Requirements
- Python 3.8+
- Google Cloud SDK (for deployment)
- Required Python packages (see `requirements.txt`)
- Instagram API credentials and tokens
- OpenAI API key

## Environment Variables
Set the following environment variables for proper operation:
- `INSTA_PAGE_ACCESS_TOKEN`: Instagram page access token
- `INSTA_PAGE_VERIFY_TOKEN`: Webhook verification token
- `INSTA_BUSINESS_ACCOUNT_ID`: Instagram business account ID
- `STABILITY_KEY`: Stability AI API key (if using image generation)
- `OPENAI_TOKEN`: OpenAI API key
- `THREADS_API_TOKEN`: Threads API token (if using Threads)
- `THREADS_USER_ID`: Threads user ID

## Deployment
Deploy to Google Cloud Run with the following command (replace project and region as needed):

```sh
gcloud run deploy ai-bot-app-insta --allow-unauthenticated --region=asia-northeast1 --project=yahayuta --source .
```

## Usage
- Start the Flask app locally for development and testing.
- Use the provided endpoints to trigger content generation and posting.
- Customize topics, patterns, and other parameters in `main.py` as desired.

## Notes
- This is an example app. You may need to adapt it for production use, including error handling, security, and API rate limits.
- Ensure all required environment variables are set before running or deploying.

---

Feel free to modify the code and configuration to suit your needs!