# AI Instagram Bot with Enhanced Prompt Engineering

A sophisticated Python-based Instagram bot that leverages multiple AI providers (OpenAI, Stability AI, Google Imagen) for automated content creation and posting. Features advanced prompt engineering with A/B testing capabilities and performance tracking.

## 🚀 Features

### Core Functionality
- **Multi-AI Image Generation**: Support for Stability AI, DALL-E 3, and Google Imagen
- **Enhanced Prompt Engineering**: Advanced prompt optimization with lighting, composition, mood, and quality enhancers
- **A/B Testing Framework**: Compare different prompt strategies and track performance
- **Automated Social Media Posting**: Post to Instagram (feed + stories) and Threads
- **Google Cloud Storage Integration**: Automatic image upload and management
- **Vision AI Caption Generation**: Use Gemini AI for intelligent image descriptions

### Advanced Prompt Features
- **16 Lighting Styles**: dramatic, golden hour, studio lighting, etc.
- **16 Composition Styles**: close-up, wide shot, rule of thirds, etc.
- **18 Mood Atmospheres**: mysterious, whimsical, melancholic, etc.
- **12 Quality Enhancers**: 8k resolution, masterpiece, trending on artstation, etc.
- **50+ Negative Prompts**: Comprehensive list to avoid common generation issues
- **AI-Specific Optimization**: Tailored prompts for each AI provider

## 🛠️ Requirements

- Python 3.8+
- Google Cloud SDK (for deployment)
- Required Python packages (see `requirements.txt`)
- Instagram API credentials and tokens
- OpenAI API key
- Stability AI API key
- Google Gemini API key

## 🔧 Environment Variables

### Core API Keys
```bash
# Instagram Configuration
INSTA_PAGE_ACCESS_TOKEN=your_instagram_page_access_token
INSTA_PAGE_VERIFY_TOKEN=your_webhook_verification_token
INSTA_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id

# AI Provider Keys
OPENAI_TOKEN=your_openai_api_key
STABILITY_KEY=your_stability_ai_key
GEMINI_API_KEY=your_google_gemini_key

# Threads Configuration (Optional)
THREADS_API_TOKEN=your_threads_api_token
THREADS_USER_ID=your_threads_user_id
```

### Prompt Tuning Configuration
```bash
# Enable/disable enhanced prompts
ENABLE_ENHANCED_PROMPTS=true
ENABLE_NEGATIVE_PROMPTS=true
ENABLE_AB_TESTING=false
PROMPT_COMPLEXITY_LEVEL=2  # 1=simple, 2=enhanced, 3=complex
```

## 📡 API Endpoints

### Content Generation Endpoints
- `GET /stability_post_insta` - Generate with Stability AI
- `GET /openai_post_insta` - Generate with DALL-E 3
- `GET /imagen_post_insta` - Generate with Google Imagen

### Testing & Analytics Endpoints
- `GET /test_prompt_strategies` - A/B test different prompt strategies
- `GET /prompt_performance` - View performance statistics
- `POST /reset_prompt_performance` - Reset performance tracking

## 🚀 Deployment

Deploy to Google Cloud Run:

```sh
gcloud run deploy ai-bot-app-insta --allow-unauthenticated --region=asia-northeast1 --project=yahayuta --source .
```

## 📊 Usage Examples

### Basic Content Generation
```bash
# Generate with Stability AI
curl http://localhost:5000/stability_post_insta

# Generate with DALL-E 3
curl http://localhost:5000/openai_post_insta

# Generate with Google Imagen
curl http://localhost:5000/imagen_post_insta
```

### A/B Testing
```bash
# Test different prompt strategies
curl http://localhost:5000/test_prompt_strategies

# Check performance stats
curl http://localhost:5000/prompt_performance

# Reset performance tracking
curl -X POST http://localhost:5000/reset_prompt_performance
```

## 🎨 Prompt Engineering

### Enhanced Prompt Structure
```
Original: "Naruto, watercolor"
Enhanced: "Naruto character, watercolor style, dramatic lighting, close-up shot, mysterious, highly detailed"
```

### AI-Specific Optimizations

#### Stability AI
- Detailed, comma-separated components
- Full negative prompt support
- Example: `"Naruto, watercolor, dramatic lighting, close-up shot, mysterious, highly detailed"`

#### DALL-E 3
- Natural language sentences
- Conversational style
- Example: `"A mysterious watercolor of Naruto with dramatic lighting and close-up shot, highly detailed"`

#### Google Imagen
- Professional, descriptive format
- Clear structure
- Example: `"Naruto in watercolor style, featuring dramatic lighting and close-up shot, mysterious atmosphere, highly detailed"`

## 📈 Performance Tracking

The system tracks:
- Success rates per strategy
- Error rates and types
- NSFW filter rates
- Generation time metrics
- A/B test results

## 🔍 Testing Strategy

### Phase 1: Basic Enhancement ✅
- Enhanced prompt components
- Negative prompts
- AI-specific optimizations

### Phase 2: Testing Framework ✅
- A/B testing endpoints
- Performance tracking
- Configuration system

### Phase 3: Advanced Features (Future)
- Dynamic prompt learning
- Style-specific optimization
- Web interface for tuning
- Quality metrics integration

## 📚 Documentation

- `PROMPT_ENHANCEMENT_PLAN.md` - Comprehensive prompt engineering guide
- `main.py` - Main application with all endpoints and functions
- `requirements.txt` - Python dependencies

## 🔒 Security & Best Practices

- Store API keys in environment variables
- Implement rate limiting for production use
- Add proper error handling and logging
- Consider API usage costs and limits
- Monitor for NSFW content filtering

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Feel free to modify and adapt for your needs!

---

**Note**: This is a demonstration app. For production use, ensure proper error handling, security measures, and API rate limit management.