import React from 'react';
import { WordDetail } from './VoxCollageScene';

export interface StorybookSceneProps {
  currentFrame: number;
  fps: number;
  heroImage: string;
  wordsDetail: WordDetail[];
}

export const StorybookScene: React.FC<StorybookSceneProps> = ({
  currentFrame,
  fps,
  heroImage,
  wordsDetail
}) => {
  const currentTimeMs = (currentFrame / fps) * 1000;
  
  // 模拟微风沉浸式呼吸悬浮动画
  const floatOffsetY = Math.sin((currentFrame / fps) * 1.5) * 6;

  return (
    <div
      style={{
        width: '1280px',
        height: '720px',
        position: 'relative',
        backgroundColor: '#FAF5EF',
        overflow: 'hidden',
        fontFamily: 'Inter, Noto Sans SC, sans-serif'
      }}
    >
      {/* 1. 水彩纸雕 Hero 主帧画面（带微风呼吸悬浮效果） */}
      <div
        style={{
          width: '100%',
          height: '100%',
          transform: `translateY(${floatOffsetY}px)`,
          transition: 'transform 0.1s linear'
        }}
      >
        <img
          src={heroImage}
          alt="Storybook Shared Hero Frame"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            borderRadius: '8px',
            boxShadow: '0 8px 24px rgba(0,0,0,0.08)'
          }}
        />
      </div>

      {/* 2. 温暖童趣画风逐字高亮字幕 */}
      <div
        style={{
          position: 'absolute',
          bottom: '40px',
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          gap: '6px',
          padding: '10px 20px',
          backgroundColor: 'rgba(255, 248, 240, 0.95)',
          borderRadius: '20px',
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.06)'
        }}
      >
        {wordsDetail.map((w, idx) => {
          const isActive = currentTimeMs >= w.start_ms && currentTimeMs <= w.end_ms;
          return (
            <span
              key={idx}
              style={{
                fontSize: '26px',
                fontWeight: '600',
                color: isActive ? '#D97706' : '#4B5563',
                transform: isActive ? 'scale(1.12)' : 'scale(1.0)',
                transition: 'transform 0.12s ease, color 0.12s ease'
              }}
            >
              {w.word}
            </span>
          );
        })}
      </div>
    </div>
  );
};
