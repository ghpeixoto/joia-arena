'use client';
import { useState, useEffect } from 'react';

export const TypingEffect = ({ text, speed = 30 }: { text: string, speed?: number }) => {
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    let currentIndex = 0;
    const intervalId = setInterval(() => {
      if (currentIndex <= text.length) {
        setDisplayedText(text.slice(0, currentIndex));
        currentIndex++;
      } else {
        clearInterval(intervalId);
      }
    }, speed);
    return () => clearInterval(intervalId);
  }, [text, speed]);

  return (
    <span>
      {displayedText}
      {displayedText.length < text.length && (
        // COR NOVA AQUI: #D946EF (Magenta Vibrante)
        <span className="inline-block w-[2px] h-[1em] bg-[#D946EF] ml-1 animate-pulse align-middle"></span>
      )}
    </span>
  );
};