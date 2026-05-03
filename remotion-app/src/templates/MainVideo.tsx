import React from 'react';
import { Sequence, Audio } from 'remotion';
import { SlideData } from './Shared';
import {
  TitleSlide,
  AgendaSlide,
  SectionDividerSlide,
  ConceptExplanationSlide,
  ComparisonSlide,
  StepByStepProcessSlide,
  DataStatisticsSlide,
  ExampleCaseStudySlide,
  SummarySlide,
  QuestionDiscussionSlide
} from './Slides';

export const MainVideo: React.FC<{ slides: SlideData[], audioUrls: string[] }> = ({ slides, audioUrls }) => {
  let currentFrameOffset = 0;
  
  return (
    <>
      {slides.map((slide, index) => {
        // Enforce a minimum duration of 3 seconds (72 frames at 24fps) for animation to complete
        const durationInFrames = Math.max(Math.ceil((slide.durationInSeconds || 5) * 24), 72);
        const startFrame = currentFrameOffset;
        currentFrameOffset += durationInFrames;
        
        const audioUrl = audioUrls[index];

        return (
          <Sequence key={index} from={startFrame} durationInFrames={durationInFrames}>
            {slide.type === 'TitleSlide' && <TitleSlide data={slide} />}
            {slide.type === 'AgendaSlide' && <AgendaSlide data={slide} />}
            {slide.type === 'SectionDividerSlide' && <SectionDividerSlide data={slide} />}
            {slide.type === 'ConceptExplanationSlide' && <ConceptExplanationSlide data={slide} />}
            {slide.type === 'ComparisonSlide' && <ComparisonSlide data={slide} />}
            {slide.type === 'StepByStepProcessSlide' && <StepByStepProcessSlide data={slide} />}
            {slide.type === 'DataStatisticsSlide' && <DataStatisticsSlide data={slide} />}
            {slide.type === 'ExampleCaseStudySlide' && <ExampleCaseStudySlide data={slide} />}
            {slide.type === 'SummarySlide' && <SummarySlide data={slide} />}
            {slide.type === 'QuestionDiscussionSlide' && <QuestionDiscussionSlide data={slide} />}
            
            {audioUrl && <Audio src={audioUrl} />}
          </Sequence>
        );
      })}
    </>
  );
};
