import React from 'react';
import { Composition } from 'remotion';
import { MainVideo } from './templates/MainVideo';
import { SlideData } from './templates/Shared';
import './index.css';

const defaultSlides: SlideData[] = [
  {
    type: 'TitleSlide',
    title: 'Understanding Neural Networks',
    subtitle: 'A Quick Introduction',
    icon: 'Brain',
    durationInSeconds: 4,
  },
  {
    type: 'ConceptExplanationSlide',
    title: 'The Core Equation',
    content: ['Neural networks use weights and biases to compute output.'],
    latex: 'y = f(W x + b)',
    icon: 'Calculator',
    durationInSeconds: 5,
  }
];

export const RemotionRoot: React.FC = () => {
  // Total duration based on sum of durations (min 3s per slide)
  const totalDuration = defaultSlides.reduce((acc, slide) => {
    return acc + Math.max(Math.ceil(slide.durationInSeconds * 30), 90);
  }, 0);

  return (
    <>
      <Composition
        id="EducationalVideo"
        component={MainVideo}
        durationInFrames={totalDuration}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          slides: defaultSlides,
          audioUrls: [],
        }}
      />
    </>
  );
};
