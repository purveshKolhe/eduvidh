# EduGen AI - Educational Video Generator

Transform your text prompts into beautifully animated, narrated, 720p educational videos in under 60 seconds!

Built for ultimate speed and cost-efficiency, EduGen leverages **Modal** for serverless compute, **Remotion** for programmatic video generation, and **Groq** for lightning-fast LLM script generation.

## 🚀 Features
- **Ultra-Fast Generation:** Generates 6-slide animated presentations in ~40 seconds.
- **Extreme Cost Efficiency:** Uses pre-bundled React code, Chrome Headless Shell, and FFmpeg `-c copy` static frame looping to drop Remotion rendering costs to fractions of a cent per video.
- **Responsive Slides:** Text dynamically scales based on length to prevent overflow.
- **Math Support:** Automatically renders complex equations using KaTeX.
- **Professional Frontend:** A sleek Next.js UI with real-time polling, glassmorphism, and client-side rate limiting.

## 🛠️ Architecture
1. **Frontend (Next.js):** Submits prompts to the webhook and polls Supabase for real-time status.
2. **Orchestrator (Modal - 1 Core):** Calls Groq (`openai/gpt-oss-20b`) for the JSON script, estimates TTS duration, and immediately fans out render workers. Generates EdgeTTS audio concurrently in the background.
3. **Render Workers (Modal - 2 Core):** Pre-bundled Remotion workers render exactly 3 seconds (24fps) of the entrance animation, use FFmpeg to extend the final static frame to the estimated duration, and return silent video chunks.
4. **Stitching:** The Orchestrator merges the generated TTS audio with the silent chunks and concatenates them instantly. The final `output.mp4` is uploaded to Supabase Storage.

## ⚙️ Local Setup Guide (Free)
You can deploy the backend entirely for free using Modal's $5 monthly credit tier.

### 1. Database Setup
1. Create a free [Supabase](https://supabase.com/) project.
2. Run the `supabase_schema.sql` file in the Supabase SQL editor to create the `videos` table and the public `video-assets` storage bucket.

### 2. Backend Deployment (Modal)
1. Get a free [Groq API Key](https://console.groq.com/).
2. Create a free [Modal Account](https://modal.com/).
3. In the root directory, create a `.env` file:
```env
GROQ_API_KEY=your_groq_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```
4. Setup the Python environment and deploy:
```bash
python -m venv venv
source venv/bin/activate
pip install modal supabase groq edge-tts
modal token new
modal deploy modal_app.py
```
Modal will output a webhook URL (e.g., `https://your-username--edu-video-generator-start-generation.modal.run`).

### 3. Frontend Deployment (Render/Vercel)
1. Navigate to the `frontend/` directory.
2. Create a `.env.local` file:
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_MODAL_WEBHOOK_URL=the_webhook_url_from_step_2
```
3. Install dependencies and run locally (or deploy to Render):
```bash
npm install
npm run build
npm run start
```

## 📜 License
This project is licensed under the **Business Source License 1.1** (BSL-1.1). You may read and test the code locally, but public deployment, forking, and commercial usage are restricted until **May 3, 2029**, at which point it automatically transitions to the MIT License. See the `LICENSE` file for details.