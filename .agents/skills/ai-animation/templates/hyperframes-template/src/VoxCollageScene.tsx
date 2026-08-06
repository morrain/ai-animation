import React from 'react';

export interface WordDetail {
  word: string;
  start_ms: number;
  end_ms: number;
}

export interface VoxCollageSceneProps {
  currentFrame: number;
  fps: number;
  bgImage: string;
  fgCharacterImage?: string;
  wordsDetail: WordDetail[];
  transitionEffect?: string;
}

export const VoxCollageScene: React.FC<VoxCollageSceneProps> = ({
  currentFrame,
  fps,
  bgImage,
  fgCharacterImage,
  wordsDetail,
  transitionEffect = 'paper_rip'
}) => {
  const currentTimeMs = (currentFrame / fps) * 1000;

  return (
    <div
      style={{
        width: '1280px',
        height: '720px',
        position: 'relative',
        backgroundColor: '#F4F1EA',
        overflow: 'hidden',
        fontFamily: 'Inter, Noto Sans SC, sans-serif'
      }}
    >
      {/* 1. 背景卡纸纹理 */}
      <img
        src={bgImage}
        alt="Background Paper Collage"
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          filter: 'contrast(1.05) brightness(0.98)'
        }}
      />

      {/* 2. 前景黑白半调人物组件 */}
      {fgCharacterImage && (
        <img
          src={fgCharacterImage}
          alt="Halftone Character"
          style={{
            position: 'absolute',
            bottom: '20px',
            right: '40px',
            maxHeight: '600px',
            filter: 'grayscale(100%) contrast(1.3)',
            dropShadow: '5px 5px 0px rgba(0,0,0,0.15)'
          }}
        />
      )}

      {/* 3. 逐字高光动态字幕 (Kinetic Typography) */}
      <div
        style={{
          position: 'absolute',
          bottom: '50px',
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          gap: '8px',
          padding: '12px 24px',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderRadius: '4px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        }}
      >
        {wordsDetail.map((w, idx) => {
          const isActive = currentTimeMs >= w.start_ms && currentTimeMs <= w.end_ms;
          return (
            <span
              key={idx}
              style={{
                fontSize: '28px',
                fontWeight: 'bold',
                color: isActive ? '#E63946' : '#1D3557',
                transform: isActive ? 'scale(1.15)' : 'scale(1.0)',
                transition: 'transform 0.1s ease, color 0.1s ease'
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
