import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import 'katex/dist/katex.min.css';
import * as Icons from 'lucide-react';

export type SlideData = {
  type: 
    | 'TitleSlide' 
    | 'AgendaSlide' 
    | 'SectionDividerSlide' 
    | 'ConceptExplanationSlide' 
    | 'ComparisonSlide' 
    | 'StepByStepProcessSlide' 
    | 'DataStatisticsSlide' 
    | 'ExampleCaseStudySlide' 
    | 'SummarySlide' 
    | 'QuestionDiscussionSlide';
  title: string;
  subtitle?: string;
  content?: string[];
  latex?: string;
  icon?: keyof typeof Icons;
  durationInSeconds: number; // dynamically passed from TTS
};

// Base Slide Layout that handles the 3-second entrance animation wrapper
export const SlideWrapper: React.FC<{ children: React.ReactNode, bgColor?: string }> = ({ children, bgColor = '#f8fafc' }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  // Opacity fade in over 0.5s (12 frames at 24 fps)
  const opacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });
  
  // Scale up with spring
  const scale = spring({
    fps,
    frame,
    config: { damping: 12, mass: 0.5 },
  });

  return (
    <AbsoluteFill style={{ backgroundColor: bgColor, justifyContent: 'center', alignItems: 'center', fontFamily: 'sans-serif', padding: '60px' }}>
      <div style={{ opacity, transform: `scale(${scale})`, width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
        {children}
      </div>
    </AbsoluteFill>
  );
};
