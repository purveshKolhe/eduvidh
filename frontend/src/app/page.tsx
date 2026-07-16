"use client";

import { useState, useEffect, FormEvent } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { createClient } from "@supabase/supabase-js";
import { Sparkles, Loader2, Video, Send, CheckCircle, AlertCircle, LayoutTemplate, Clock } from "lucide-react";

// Initialize Supabase Client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_URL.startsWith("http") 
  ? process.env.NEXT_PUBLIC_SUPABASE_URL 
  : "https://placeholder.supabase.co";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "placeholder";
const webhookUrl = process.env.NEXT_PUBLIC_WEBHOOK_URL || process.env.NEXT_PUBLIC_MODAL_WEBHOOK_URL || "";

const supabase = createClient(supabaseUrl, supabaseAnonKey);

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("idle");
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // Timer Effect
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (jobId && status !== "completed" && status !== "failed") {
      interval = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
    } else if (status === "idle") {
      setElapsedSeconds(0);
    }
    return () => clearInterval(interval);
  }, [jobId, status]);

  // Polling Effect
  useEffect(() => {
    if (!jobId || status === "completed" || status === "failed") return;

    const interval = setInterval(async () => {
      if (!supabaseUrl || supabaseUrl === "https://placeholder.supabase.co") {
        return;
      }
      
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
    }, 3000);

    return () => clearInterval(interval);
  }, [jobId, status]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setStatus("submitting");
    setErrorMessage(null);
    setJobId(null);
    setVideoUrl(null);
    setElapsedSeconds(0);

    try {
      if (!webhookUrl) {
        throw new Error("Webhook URL is not configured. Please check your environment variables.");
      }

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

  const getPhaseMessage = () => {
    if (elapsedSeconds < 15) return "Creating script...";
    if (elapsedSeconds < 22) return "Converting to JSON...";
    if (elapsedSeconds < 37) return "Fanning out the GPUs...";
    if (elapsedSeconds < 52) return "Generating your TTS...";
    return "Rendering your video / upscaling it...";
  };

  const countdownValue = Math.max(0, 60 - elapsedSeconds);
  const minutes = Math.floor(countdownValue / 60);
  const seconds = countdownValue % 60;
  const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900 selection:bg-pink-200">
      {/* Navbar */}
      <header className="fixed top-0 w-full z-50 bg-white/70 backdrop-blur-lg border-b border-slate-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-xl tracking-tight text-indigo-950">
            <LayoutTemplate className="w-6 h-6 text-pink-500" />
            EduGen AI(Part of Luvia)
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow flex flex-col items-center justify-center p-6 relative overflow-hidden pt-24 pb-12">
        {/* Background Gradients */}
        <div className="absolute top-0 -left-20 w-[30rem] h-[30rem] bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
        <div className="absolute top-40 -right-20 w-[30rem] h-[30rem] bg-indigo-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-40 left-1/2 -translate-x-1/2 w-[30rem] h-[30rem] bg-violet-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>

        <div className="z-10 w-full max-w-3xl mx-auto relative flex flex-col items-center">
          
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="text-center mb-10 w-full"
          >
            <div className="inline-flex items-center justify-center space-x-2 bg-indigo-50 px-4 py-1.5 rounded-full border border-indigo-100 mb-8 text-indigo-700 font-semibold tracking-wide text-xs uppercase shadow-sm">
              <Sparkles className="w-3.5 h-3.5 mr-1 text-pink-500" /> Powered by Luvia AI
            </div>
            <h1 className="text-5xl md:text-7xl font-extrabold text-transparent bg-clip-text bg-gradient-to-br from-indigo-950 via-slate-800 to-pink-700 tracking-tight leading-[1.1] pb-2">
              Transform Ideas into <br className="hidden md:block"/> Educational Videos
            </h1>
            <p className="mt-6 text-lg text-slate-500 max-w-2xl mx-auto font-medium">
              Enter a topic and our heavily optimized AI pipeline will generate a 720p narrated, animated presentation in under 60 seconds.
            </p>
          </motion.div>

          {/* Form */}
          <AnimatePresence mode="wait">
            {(status === "idle" || status === "submitting" || status === "failed") && (
              <motion.form
                key="form"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.95 }}
                transition={{ duration: 0.4 }}
                onSubmit={handleSubmit}
                className="w-full max-w-2xl"
              >
                <div className="relative group">
                  <div className="absolute -inset-1 bg-gradient-to-r from-pink-300 via-indigo-300 to-violet-300 rounded-[2rem] blur opacity-30 group-hover:opacity-50 transition duration-500"></div>
                  <div className="relative bg-white/80 backdrop-blur-2xl rounded-[2rem] p-3 shadow-xl border border-white flex flex-col gap-3">
                    <textarea
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      disabled={status === "submitting"}
                      placeholder="e.g. Explain the mechanics of a black hole..."
                      className="w-full bg-transparent resize-none outline-none px-5 py-4 text-slate-800 placeholder:text-slate-400 font-medium text-lg min-h-[120px]"
                    />
                    
                    <div className="flex items-center justify-between px-3 pb-1">
                      <div className="flex items-center text-sm font-semibold text-slate-500">
                        <span className="flex items-center text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full">Unlimited videos today</span>
                      </div>
                      <button
                        type="submit"
                        disabled={!prompt.trim() || status === "submitting"}
                        className="h-12 px-8 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold shadow-md shadow-indigo-200 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-indigo-600 group/btn"
                      >
                        {status === "submitting" ? (
                          <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                          <>
                            Generate
                            <Send className="w-4 h-4 ml-2 group-hover/btn:translate-x-1 group-hover/btn:-translate-y-0.5 transition-transform" />
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
                {errorMessage && (
                  <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mt-6 text-center text-rose-600 bg-rose-50/80 backdrop-blur-md rounded-2xl p-4 border border-rose-100 shadow-sm font-medium">
                    {errorMessage}
                  </motion.div>
                )}
              </motion.form>
            )}
          </AnimatePresence>

          {/* Countdown / Polling Dashboard */}
          <AnimatePresence>
            {status !== "idle" && status !== "submitting" && status !== "failed" && status !== "completed" && (
              <motion.div
                key="status"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-2xl bg-white/90 backdrop-blur-3xl border border-white rounded-[2.5rem] p-12 shadow-2xl flex flex-col items-center justify-center min-h-[400px] relative overflow-hidden"
              >
                {/* Circular Progress Background */}
                <div className="absolute inset-0 flex items-center justify-center opacity-[0.03] pointer-events-none">
                   <Clock className="w-96 h-96 text-indigo-900" />
                </div>

                <div className="relative flex flex-col items-center">
                  <motion.div 
                    initial={{ scale: 0.5, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="text-8xl md:text-9xl font-black text-transparent bg-clip-text bg-gradient-to-b from-indigo-600 to-indigo-950 tabular-nums tracking-tighter"
                  >
                    {timeString}
                  </motion.div>
                  
                  <motion.div 
                    key={getPhaseMessage()}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-8 text-2xl font-bold text-slate-800 flex items-center gap-3"
                  >
                    <Loader2 className="w-6 h-6 animate-spin text-pink-500" />
                    {getPhaseMessage()}
                  </motion.div>

                  <p className="mt-4 text-slate-500 font-medium text-center max-w-xs leading-relaxed">
                    Please wait while our high-performance cluster prepares your educational video.
                  </p>
                  <p className="mt-2 text-slate-400 text-xs font-semibold uppercase tracking-wider text-center">
                    It could take 1-2 minutes. Have patience.
                  </p>
                </div>

                {/* Bottom Progress Bar */}
                <div className="absolute bottom-0 left-0 w-full h-2 bg-slate-100">
                  <motion.div 
                    initial={{ width: "0%" }}
                    animate={{ width: `${Math.min(100, (elapsedSeconds / 60) * 100)}%` }}
                    className="h-full bg-gradient-to-r from-indigo-500 via-pink-500 to-indigo-500"
                  />
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
                className="w-full mt-4 flex flex-col items-center"
              >
                <div className="relative group rounded-[1.5rem] overflow-hidden shadow-2xl border-[6px] border-white bg-slate-900 aspect-video w-full max-w-4xl flex items-center justify-center">
                  <div className="absolute inset-0 flex items-center justify-center -z-10 bg-slate-100">
                    <Video className="w-12 h-12 text-slate-300" />
                  </div>
                  <video 
                    src={videoUrl} 
                    controls 
                    autoPlay 
                    className="w-full h-full object-contain z-10"
                  />
                </div>
                <button 
                  onClick={() => { setStatus("idle"); setPrompt(""); setJobId(null); setVideoUrl(null); }}
                  className="mt-10 px-8 py-3.5 bg-white hover:bg-slate-50 text-slate-800 rounded-full font-bold border border-slate-200 shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5"
                >
                  Create Another Video
                </button>
              </motion.div>
            )}
          </AnimatePresence>

        </div>
      </main>

      {/* Footer */}
      <footer className="w-full py-6 text-center text-slate-500 font-medium text-sm border-t border-slate-200 bg-white/50 backdrop-blur-md relative z-10">
        Built for ultimate cost efficiency and speed.
      </footer>
    </div>
  );
}
