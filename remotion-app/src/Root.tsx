import React, { useState, useEffect, useRef } from 'react';
import { Composition, getInputProps } from 'remotion';
import { Player, PlayerRef } from '@remotion/player';
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

type VideoProps = { slides: SlideData[]; audioUrls: string[] };

type PersistentRendererWindow = Window & typeof globalThis & {
  remotion_mode?: string;
  remotion_setProps?: (newProps: VideoProps) => void;
  remotion_onPropsSet?: () => void;
  remotion_setFrame?: (frame: number) => void;
  remotion_onFrameSet?: () => void;
  remotion_ready?: boolean;
  remotion_onReady?: () => void;
};

const isVideoProps = (value: unknown): value is VideoProps => {
  if (!value || typeof value !== 'object') return false;
  const props = value as Record<string, unknown>;
  return Array.isArray(props.slides) && Array.isArray(props.audioUrls);
};

const getSafeInputProps = (): VideoProps => {
  try {
    const props = getInputProps();
    if (isVideoProps(props)) {
      return props;
    }
  } catch {
    // Ignore error
  }
  return { slides: defaultSlides, audioUrls: [] };
};

export const RemotionRoot: React.FC = () => {
  const [isPersistentMode, setIsPersistentMode] = useState(false);
  const [props, setProps] = useState<VideoProps>(() => {
    return getSafeInputProps();
  });
  const playerRef = useRef<PlayerRef>(null);

  useEffect(() => {
    const rendererWindow = window as PersistentRendererWindow;
    const params = new URLSearchParams(window.location.search);
    if (params.get('mode') === 'persistent' || rendererWindow.remotion_mode === 'persistent') {
      setIsPersistentMode(true);
    }

    rendererWindow.remotion_setProps = (newProps: VideoProps) => {
      setProps(newProps);
      setTimeout(() => {
        if (rendererWindow.remotion_onPropsSet) {
          rendererWindow.remotion_onPropsSet();
        }
      }, 100);
    };

    rendererWindow.remotion_setFrame = (frame: number) => {
      const seek = () => {
        if (playerRef.current) {
          try {
            playerRef.current.seekTo(frame);
            setTimeout(() => {
              if (rendererWindow.remotion_onFrameSet) {
                rendererWindow.remotion_onFrameSet();
              }
            }, 30);
          } catch (err) {
            console.error("seekTo error:", err);
            setTimeout(seek, 20);
          }
        } else {
          setTimeout(seek, 20);
        }
      };
      seek();
    };

    rendererWindow.remotion_ready = true;
    if (rendererWindow.remotion_onReady) {
      rendererWindow.remotion_onReady();
    }
  }, []);

  // Total duration based on sum of durations (min 3s per slide) at 24 fps
  const totalDuration = props.slides.reduce((acc, slide) => {
    return acc + Math.max(Math.ceil((slide.durationInSeconds || 5) * 24), 72);
  }, 0);

  if (isPersistentMode) {
    return (
      <div style={{ width: '1280px', height: '720px', overflow: 'hidden', position: 'relative' }}>
        <Player
          ref={playerRef}
          component={MainVideo}
          inputProps={props}
          durationInFrames={totalDuration}
          fps={24}
          compositionWidth={1280}
          compositionHeight={720}
          style={{ width: 1280, height: 720 }}
          controls={false}
          loop={false}
          autoPlay={false}
        />
      </div>
    );
  }

  return (
    <>
      <Composition
        id="EducationalVideo"
        component={MainVideo}
        durationInFrames={totalDuration}
        fps={24}
        width={1280}
        height={720}
        defaultProps={props}
      />
    </>
  );
};
