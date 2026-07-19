import React from 'react';
import { SlideData, SlideWrapper } from './Shared';
import Latex from 'react-latex-next';
import * as Icons from 'lucide-react';
import { interpolate, useCurrentFrame } from 'remotion';

// Helper to render icon safely
const RenderIcon = ({ name, size = 64, color = '#3b82f6' }: { name?: string, size?: number, color?: string }) => {
  if (!name) return null;
  const IconComponent = Icons[name as keyof typeof Icons] as React.ComponentType<{
    size?: number;
    color?: string;
  }> | undefined;
  return IconComponent ? <IconComponent size={size} color={color} /> : null;
};

export const TitleSlide: React.FC<{ data: SlideData }> = ({ data }) => (
  <SlideWrapper bgColor="#ffedd5">
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center' }}>
      <RenderIcon name={data.icon} size={120} color="#f97316" />
      <h1 style={{ fontSize: '80px', color: '#431407', marginTop: '40px', fontWeight: 'bold' }}>{data.title}</h1>
      {data.subtitle && <h2 style={{ fontSize: '40px', color: '#9a3412', marginTop: '20px' }}>{data.subtitle}</h2>}
    </div>
  </SlideWrapper>
);

export const AgendaSlide: React.FC<{ data: SlideData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const numItems = data.content?.length || 0;
  // Reduce font size and margin if there are many items
  const itemFontSize = numItems > 6 ? '30px' : numItems > 4 ? '35px' : '45px';
  const marginB = numItems > 6 ? '15px' : '30px';

  return (
    <SlideWrapper bgColor="#e0e7ff">
      <h1 style={{ fontSize: '70px', color: '#312e81', borderBottom: '8px solid #4f46e5', paddingBottom: '20px' }}>{data.title}</h1>
      <ul style={{ listStyleType: 'none', padding: 0, marginTop: '40px' }}>
        {data.content?.map((item, i) => {
          const itemOpacity = interpolate(frame, [i * 8, i * 8 + 12], [0, 1], { extrapolateRight: 'clamp' });
          const itemY = interpolate(frame, [i * 8, i * 8 + 12], [30, 0], { extrapolateRight: 'clamp' });
          return (
            <li key={i} style={{ opacity: itemOpacity, transform: `translateY(${itemY}px)`, fontSize: itemFontSize, color: '#3730a3', marginBottom: marginB, display: 'flex', alignItems: 'center' }}>
              <span style={{ backgroundColor: '#4f46e5', color: 'white', borderRadius: '50%', minWidth: '50px', height: '50px', display: 'inline-flex', justifyContent: 'center', alignItems: 'center', marginRight: '20px', fontSize: '25px', fontWeight: 'bold' }}>{i + 1}</span>
              {item}
            </li>
          );
        })}
      </ul>
    </SlideWrapper>
  );
};

export const SectionDividerSlide: React.FC<{ data: SlideData }> = ({ data }) => (
  <SlideWrapper bgColor="#4f46e5">
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center' }}>
      <h1 style={{ fontSize: '90px', color: 'white', fontWeight: 'bold', textShadow: '4px 4px 0px #312e81' }}>{data.title}</h1>
      {data.subtitle && <h2 style={{ fontSize: '45px', color: '#c7d2fe', marginTop: '20px' }}>{data.subtitle}</h2>}
    </div>
  </SlideWrapper>
);

export const ConceptExplanationSlide: React.FC<{ data: SlideData }> = ({ data }) => {
  const contentLen = data.content?.join(' ').length || 0;
  // Reduce font size dynamically based on length of text
  const pFontSize = contentLen > 300 ? '24px' : contentLen > 150 ? '32px' : '45px';
  
  let cleanLatex = '';
  if (data.latex) {
    cleanLatex = Array.isArray(data.latex) ? data.latex.join(' ') : String(data.latex);
    cleanLatex = cleanLatex.replace(/\$/g, '');
  }

  return (
    <SlideWrapper bgColor="#fce7f3">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '6px solid #db2777', paddingBottom: '20px', marginBottom: '40px' }}>
        <h1 style={{ fontSize: '60px', color: '#831843', margin: 0 }}>{data.title}</h1>
        <RenderIcon name={data.icon} size={80} color="#db2777" />
      </div>
      <div style={{ fontSize: pFontSize, color: '#9d174d', lineHeight: '1.6' }}>
        {data.content?.map((p, i) => <p key={i}>{p}</p>)}
        {cleanLatex && (
          <div style={{ marginTop: '30px', padding: '20px', backgroundColor: 'white', borderRadius: '20px', boxShadow: '0 10px 25px rgba(219,39,119,0.2)', textAlign: 'center', fontSize: '40px' }}>
            <Latex>{`$$${cleanLatex}$$`}</Latex>
          </div>
        )}
      </div>
    </SlideWrapper>
  );
};

export const ComparisonSlide: React.FC<{ data: SlideData }> = ({ data }) => (
  <SlideWrapper bgColor="#dcfce7">
    <h1 style={{ fontSize: '60px', color: '#14532d', textAlign: 'center', marginBottom: '60px' }}>{data.title}</h1>
    <div style={{ display: 'flex', gap: '40px', flex: 1 }}>
      <div style={{ flex: 1, backgroundColor: 'white', borderRadius: '30px', padding: '40px', boxShadow: '0 10px 30px rgba(34,197,94,0.1)' }}>
        <h2 style={{ fontSize: '45px', color: '#166534', borderBottom: '4px solid #22c55e', paddingBottom: '10px' }}>{data.content?.[0]}</h2>
        <p style={{ fontSize: '30px', color: '#15803d', marginTop: '20px' }}>{data.content?.[1]}</p>
      </div>
      <div style={{ flex: 1, backgroundColor: 'white', borderRadius: '30px', padding: '40px', boxShadow: '0 10px 30px rgba(34,197,94,0.1)' }}>
        <h2 style={{ fontSize: '45px', color: '#166534', borderBottom: '4px solid #22c55e', paddingBottom: '10px' }}>{data.content?.[2]}</h2>
        <p style={{ fontSize: '30px', color: '#15803d', marginTop: '20px' }}>{data.content?.[3]}</p>
      </div>
    </div>
  </SlideWrapper>
);

export const StepByStepProcessSlide: React.FC<{ data: SlideData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const numItems = data.content?.length || 0;
  const itemFontSize = numItems > 5 ? '26px' : '40px';
  const paddingSize = numItems > 5 ? '20px' : '30px';

  return (
    <SlideWrapper bgColor="#fef3c7">
      <h1 style={{ fontSize: '65px', color: '#78350f', textAlign: 'center', marginBottom: '50px' }}>{data.title}</h1>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', flex: 1, justifyContent: 'center' }}>
        {data.content?.map((step, i) => {
          const itemOpacity = interpolate(frame, [i * 12, i * 12 + 12], [0, 1], { extrapolateRight: 'clamp' });
          const itemX = interpolate(frame, [i * 12, i * 12 + 12], [-50, 0], { extrapolateRight: 'clamp' });
          return (
            <div key={i} style={{ opacity: itemOpacity, transform: `translateX(${itemX}px)`, backgroundColor: 'white', borderRadius: '20px', padding: paddingSize, display: 'flex', alignItems: 'center', boxShadow: '0 8px 20px rgba(217,119,6,0.1)' }}>
              <div style={{ backgroundColor: '#f59e0b', color: 'white', borderRadius: '15px', minWidth: '60px', height: '60px', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '30px', fontWeight: 'bold', marginRight: '20px' }}>{i + 1}</div>
              <span style={{ fontSize: itemFontSize, color: '#92400e' }}>{step}</span>
            </div>
          );
        })}
      </div>
    </SlideWrapper>
  );
};

export const DataStatisticsSlide: React.FC<{ data: SlideData }> = ({ data }) => (
  <SlideWrapper bgColor="#e0f2fe">
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
      <h2 style={{ fontSize: '50px', color: '#0369a1', marginBottom: '20px' }}>{data.title}</h2>
      <div style={{ fontSize: '130px', fontWeight: 'bold', color: '#0284c7', textShadow: '5px 5px 0px #bae6fd' }}>
        {data.content?.[0] || '100%'}
      </div>
      <p style={{ fontSize: '35px', color: '#0c4a6e', marginTop: '30px', textAlign: 'center', maxWidth: '80%' }}>
        {data.content?.[1]}
      </p>
      {data.icon && <div style={{ marginTop: '50px' }}><RenderIcon name={data.icon} size={100} color="#0284c7" /></div>}
    </div>
  </SlideWrapper>
);

export const ExampleCaseStudySlide: React.FC<{ data: SlideData }> = ({ data }) => {
  const contentLen = data.content?.join(' ').length || 0;
  const pFontSize = contentLen > 300 ? '24px' : contentLen > 150 ? '30px' : '40px';

  return (
    <SlideWrapper bgColor="#f3e8ff">
      <div style={{ border: '8px dashed #a855f7', borderRadius: '40px', padding: '50px', flex: 1, display: 'flex', flexDirection: 'column', backgroundColor: 'rgba(255,255,255,0.6)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '30px', marginBottom: '40px' }}>
          <div style={{ backgroundColor: '#a855f7', color: 'white', padding: '10px 20px', borderRadius: '20px', fontSize: '30px', fontWeight: 'bold' }}>Example</div>
          <h1 style={{ fontSize: '55px', color: '#581c87', margin: 0 }}>{data.title}</h1>
        </div>
        <div style={{ fontSize: pFontSize, color: '#6b21a8', lineHeight: '1.7', flex: 1 }}>
          {data.content?.map((p, i) => <p key={i}>{p}</p>)}
        </div>
      </div>
    </SlideWrapper>
  );
};

export const SummarySlide: React.FC<{ data: SlideData }> = ({ data }) => {
  const contentLen = data.content?.join(' ').length || 0;
  const numItems = data.content?.length || 0;
  
  const itemFontSize = contentLen > 300 ? '26px' : (contentLen > 150 || numItems > 5) ? '32px' : '45px';
  const marginB = (contentLen > 200 || numItems > 5) ? '15px' : '30px';

  return (
    <SlideWrapper bgColor="#ecfdf5">
      <h1 style={{ fontSize: '70px', color: '#064e3b', textAlign: 'center', marginBottom: '50px' }}>{data.title}</h1>
      <div style={{ backgroundColor: '#10b981', color: 'white', borderRadius: '30px', padding: '60px', flex: 1, boxShadow: '0 15px 35px rgba(16,185,129,0.3)' }}>
        <ul style={{ listStyleType: 'none', padding: 0, margin: 0 }}>
          {data.content?.map((item, i) => (
            <li key={i} style={{ fontSize: itemFontSize, marginBottom: marginB, display: 'flex', alignItems: 'flex-start' }}>
              <span style={{ marginRight: '20px', color: '#a7f3d0' }}>✔</span>
              {item}
            </li>
          ))}
        </ul>
      </div>
    </SlideWrapper>
  );
};

export const QuestionDiscussionSlide: React.FC<{ data: SlideData }> = ({ data }) => (
  <SlideWrapper bgColor="#fef2f2">
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center' }}>
      <RenderIcon name="MessageCircleQuestion" size={150} color="#ef4444" />
      <h1 style={{ fontSize: '80px', color: '#7f1d1d', marginTop: '60px', fontWeight: 'bold', lineHeight: '1.2', maxWidth: '90%' }}>
        {data.title}
      </h1>
      {data.subtitle && <p style={{ fontSize: '45px', color: '#b91c1c', marginTop: '40px', fontStyle: 'italic' }}>{data.subtitle}</p>}
    </div>
  </SlideWrapper>
);
