import { useState, useRef, useEffect } from 'react';
import { IconButton, Box, LinearProgress } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';

function AudioPlayer({ audioUrl }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const audioRef = useRef(new Audio());

  useEffect(() => {
    const audio = audioRef.current;
    
    if (audioUrl) {
      audio.src = audioUrl;
      audio.load();
    }

    const updateProgress = () => {
      if (audio.duration) {
        setProgress((audio.currentTime / audio.duration) * 100);
      }
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setProgress(0);
    };

    audio.addEventListener('timeupdate', updateProgress);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.pause();
      audio.removeEventListener('timeupdate', updateProgress);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [audioUrl]);

  const togglePlayback = () => {
    const audio = audioRef.current;
    
    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    
    setIsPlaying(!isPlaying);
  };

  if (!audioUrl) return null;

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1, gap: 1 }}>
      <IconButton 
        size="small" 
        onClick={togglePlayback}
        color="primary"
      >
        {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
      </IconButton>
      <LinearProgress 
        variant="determinate" 
        value={progress} 
        sx={{ 
          flexGrow: 1, 
          height: 4, 
          borderRadius: 2,
          backgroundColor: 'rgba(25, 118, 210, 0.1)'
        }} 
      />
    </Box>
  );
}

export default AudioPlayer;