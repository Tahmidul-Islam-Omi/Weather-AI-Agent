import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import { Box, CircularProgress, IconButton, Tooltip, Typography } from '@mui/material';
import { useEffect, useRef, useState } from 'react';

function VoiceRecorder({ onRecordingComplete, disabled }) {
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const timerRef = useRef(null);

    // Clean up timer on unmount
    useEffect(() => {
        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
        };
    }, []);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });
            
            // Use a more compatible audio format
            const options = { mimeType: 'audio/webm' };
            const mediaRecorder = new MediaRecorder(stream, options);
            
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];
            setRecordingTime(0);

            // Start a timer to track recording duration
            timerRef.current = setInterval(() => {
                setRecordingTime(prev => prev + 1);
            }, 1000);

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                setIsProcessing(true);
                
                // Clear the timer
                if (timerRef.current) {
                    clearInterval(timerRef.current);
                }
                
                // Create audio blob from chunks
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

                const audioUrl = URL.createObjectURL(audioBlob);
                
                console.log('Recording created:', audioUrl);
                
                try {
                    // Pass the original blob to the parent component - don't try to convert it
                    await onRecordingComplete(audioBlob);
                } catch (error) {
                    console.error('Error processing recording:', error);
                } finally {
                    setIsProcessing(false);
                }

                // Stop all tracks in the stream
                stream.getTracks().forEach(track => track.stop());
            };

            // Request data every 1 second to ensure we capture everything
            mediaRecorder.start(1000);
            setIsRecording(true);
        } catch (error) {
            console.error('Error starting recording:', error);
            alert('Could not access microphone. Please check permissions.');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    // Format seconds to MM:SS
    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
        const secs = (seconds % 60).toString().padStart(2, '0');
        return `${mins}:${secs}`;
    };

    return (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {isRecording && (
                <Typography 
                    variant="caption" 
                    color="error" 
                    sx={{ mr: 1, animation: 'pulse 1.5s infinite' }}
                >
                    {formatTime(recordingTime)}
                </Typography>
            )}
            
            <Tooltip title={isRecording ? "Stop recording" : "Record voice message"}>
                <span>
                    <IconButton
                        color={isRecording ? "error" : "primary"}
                        onClick={isRecording ? stopRecording : startRecording}
                        disabled={disabled || isProcessing}
                        sx={{
                            backgroundColor: isRecording ? 'rgba(244, 67, 54, 0.1)' : 'rgba(25, 118, 210, 0.1)',
                            '&:hover': {
                                backgroundColor: isRecording ? 'rgba(244, 67, 54, 0.2)' : 'rgba(25, 118, 210, 0.2)',
                            },
                            ...(isRecording && {
                                animation: 'pulse 1.5s infinite',
                                '@keyframes pulse': {
                                    '0%': { boxShadow: '0 0 0 0 rgba(244, 67, 54, 0.4)' },
                                    '70%': { boxShadow: '0 0 0 10px rgba(244, 67, 54, 0)' },
                                    '100%': { boxShadow: '0 0 0 0 rgba(244, 67, 54, 0)' }
                                }
                            })
                        }}
                    >
                        {isProcessing ? (
                            <CircularProgress size={24} color="inherit" />
                        ) : isRecording ? (
                            <StopIcon />
                        ) : (
                            <MicIcon />
                        )}
                    </IconButton>
                </span>
            </Tooltip>
        </Box>
    );
}

export default VoiceRecorder;