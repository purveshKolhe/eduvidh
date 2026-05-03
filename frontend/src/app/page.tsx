"use client";

import { useState, useEffect, FormEvent } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { createClient } from "@supabase/supabase-js";
import { Sparkles, Loader2, Video, Send, CheckCircle, AlertCircle } from "lucide-react";

// Initialize Supabase Client (fallback for prerendering without valid env vars)
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_URL.startsWith("http") 
  ? process.env.NEXT_PUBLIC_SUPABASE_URL 
  : "https://placeholder.supabase.co";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "placeholder";
const webhookUrl = process.env.NEXT_PUBLIC_MODAL_WEBHOOK_URL || "";

const supabase = createClient(supabaseUrl, supabaseAnonKey);

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("idle");
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Polling Effect
  useEffect(() => {
    if (!jobId || status === "completed" || status === "failed") return;

    const interval = setInterval(async () => {
      if (!supabaseUrl) return; // Missing credentials protection
      
      const { data, error } = await supabase
        .from("videos")
        .select("status, video_url, error_message")
        .eq("id", jobId)
        .single();

      if (error) {
        console.error("Polling error:", error);
        return;
      }

      if (data) {
        setStatus(data.status);
        if (data.status === "completed" && data.video_url) {
          setVideoUrl(data.video_url);
        }
        if (data.status === "failed") {
          setErrorMessage(data.error_message || "An unknown error occurred.");
        }
      }
    }, 3000); // Poll every 3 seconds

    return () => clearInterval(interval);
  }, [jobId, status]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setStatus("submitting");
    setErrorMessage(null);
    setJobId(null);
    setVideoUrl(null);

    try {
      const res = await fetch(webhookUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      const data = await res.json();
      
      if (data.error) throw new Error(data.error);

      setJobId(data.job_id);
      setStatus("pending");
    } catch (err: any) {
      setStatus("failed");
      setErrorMessage(err.message || "Failed to start job.");
    }
  };

  const getStatusText = () => {
    switch (status) {
      case "submitting": return "Awakening the AI...";
      case "pending": return "Preparing the studio...";
      case "script_generated": return "Writing an engaging script...";
      case "audio_generated": return "Synthesizing narration...";
      case "rendering": return "Rendering beautiful visuals...";
      case "completed": return "Your video is ready!";
      case "failed": return "Oh no, something went wrong.";
      default: return "Ready to create";
    }
  };

  const getStatusIcon = () => {
    if (status === "failed") return <AlertCircle className="text-rose-500 w-8 h-8" />;
    if (status === "completed") return <CheckCircle className="text-emerald-500 w-8 h-8" />;
    return <Loader2 className="text-pink-500 w-8 h-8 animate-spin" />;
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-pink-50 flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Decorative Orbs */}
      <div className="absolute top-10 -left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
      <div className="absolute top-40 -right-20 w-72 h-72 bg-indigo-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
      <div className="absolute -bottom-20 left-40 w-72 h-72 bg-rose-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>

      <div className="z-10 w-full max-w-2xl relative">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center justify-center space-x-2 bg-white/60 backdrop-blur-md px-4 py-2 rounded-full border border-pink-100 shadow-sm mb-6 text-pink-600 font-medium tracking-wide text-sm">
            <Sparkles className="w-4 h-4 mr-2" /> AI Educational Video Generator
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-900 to-pink-700 tracking-tight leading-tight">
            What do you want to <br /> teach today?
          </h1>
        </motion.div>

        {/* Input Form */}
        <AnimatePresence mode="wait">
          {(status === "idle" || status === "submitting" || status === "failed") && (
            <motion.form
              key="form"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ duration: 0.4 }}
              onSubmit={handleSubmit}
              className="relative group"
            >
              <div className="absolute -inset-1 bg-gradient-to-r from-pink-300 to-indigo-300 rounded-[2rem] blur opacity-25 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-white/70 backdrop-blur-xl rounded-[2rem] p-4 shadow-xl border border-white/50 flex flex-col sm:flex-row gap-4">
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  disabled={status === "submitting"}
                  placeholder="e.g. Explain quantum computing like I'm 5..."
                  className="w-full bg-transparent resize-none outline-none px-4 py-3 text-indigo-950 placeholder:text-indigo-300 font-medium text-lg min-h-[80px]"
                />
                <div className="flex items-end justify-end">
                  <button
                    type="submit"
                    disabled={!prompt.trim() || status === "submitting"}
                    className="h-14 px-8 bg-gradient-to-r from-pink-500 to-rose-400 hover:from-pink-600 hover:to-rose-500 text-white rounded-2xl font-bold text-lg shadow-lg shadow-pink-200 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed group/btn"
                  >
                    {status === "submitting" ? (
                      <Loader2 className="w-6 h-6 animate-spin" />
                    ) : (
                      <>
                        Generate
                        <Send className="w-5 h-5 ml-2 group-hover/btn:translate-x-1 transition-transform" />
                      </>
                    )}
                  </button>
                </div>
              </div>
              {errorMessage && (
                <div className="mt-4 text-center text-rose-500 bg-rose-50/50 backdrop-blur-md rounded-xl p-3 border border-rose-100">
                  {errorMessage}
                </div>
              )}
            </motion.form>
          )}
        </AnimatePresence>

        {/* Loading / Status Dashboard */}
        <AnimatePresence>
          {status !== "idle" && status !== "submitting" && status !== "failed" && status !== "completed" && (
            <motion.div
              key="status"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.5 }}
              className="mt-8 bg-white/60 backdrop-blur-xl border border-white/60 rounded-[2rem] p-8 shadow-2xl flex flex-col items-center justify-center min-h-[300px] relative overflow-hidden"
            >
               <div className="absolute top-0 left-0 w-full h-1 bg-indigo-50">
                 <div className="h-full bg-gradient-to-r from-pink-400 to-indigo-400 animate-pulse w-1/2 rounded-full"></div>
               </div>
              {getStatusIcon()}
              <h3 className="mt-6 text-2xl font-bold text-indigo-900">{getStatusText()}</h3>
              <p className="text-indigo-400 mt-2 font-medium">This usually takes 1-2 minutes.</p>
              
              <div className="mt-8 flex gap-3 text-sm font-medium">
                 <div className={`px-3 py-1 rounded-full ${status === 'pending' ? 'bg-pink-100 text-pink-600' : 'bg-indigo-50 text-indigo-300'}`}>Queue</div>
                 <div className={`px-3 py-1 rounded-full ${status === 'script_generated' ? 'bg-pink-100 text-pink-600' : 'bg-indigo-50 text-indigo-300'}`}>Scripting</div>
                 <div className={`px-3 py-1 rounded-full ${status === 'rendering' ? 'bg-pink-100 text-pink-600' : 'bg-indigo-50 text-indigo-300'}`}>Rendering</div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Completed Video Player */}
        <AnimatePresence>
          {status === "completed" && videoUrl && (
            <motion.div
              key="video"
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ type: "spring", bounce: 0.4, duration: 0.8 }}
              className="mt-8 flex flex-col items-center"
            >
              <div className="relative group rounded-[2rem] overflow-hidden shadow-2xl border-4 border-white/80 bg-black/5 aspect-video w-full max-w-4xl flex items-center justify-center">
                {/* Fallback overlay before video loads */}
                <div className="absolute inset-0 flex items-center justify-center -z-10 bg-indigo-50">
                   <Video className="w-16 h-16 text-indigo-200" />
                </div>
                <video 
                  src={videoUrl} 
                  controls 
                  autoPlay 
                  className="w-full h-full object-cover z-10"
                />
              </div>
              <button 
                onClick={() => { setStatus("idle"); setPrompt(""); setJobId(null); setVideoUrl(null); }}
                className="mt-8 px-8 py-3 bg-white hover:bg-indigo-50 text-indigo-600 rounded-full font-semibold border border-indigo-100 shadow-sm transition-colors"
              >
                Create Another Video
              </button>
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </main>
  );
}
