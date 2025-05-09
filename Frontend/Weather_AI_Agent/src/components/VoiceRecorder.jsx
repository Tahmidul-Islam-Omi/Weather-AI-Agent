import { useState, useRef } from 'react';
import { IconButton, CircularProgress, Tooltip } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';

function VoiceRecorder({ onRecordingComplete, disabled }) {
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                setIsProcessing(true);
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });

                try {
                    await onRecordingComplete(audioBlob);
                } catch (error) {
                    console.error('Error processing recording:', error);
                } finally {
                    setIsProcessing(false);
                }

                // Stop all tracks in the stream
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
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

    return (
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
                        }
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
    );
}

export default VoiceRecorder;