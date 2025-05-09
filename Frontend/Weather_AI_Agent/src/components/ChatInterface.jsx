import { useState, useRef, useEffect } from 'react';
import {
    Box,
    Paper,
    TextField,
    IconButton,
    Typography,
    CircularProgress,
    Divider
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import MessageList from './MessageList';
import VoiceRecorder from './VoiceRecorder';
import { sendMessage } from '../services/api';
import { convertSpeechToText, convertTextToSpeech } from '../services/voiceService';

function ChatInterface() {
    const [messages, setMessages] = useState([
        {
            id: 1,
            text: "Hello! I'm your Weather AI Assistant. Ask me about the weather anywhere!",
            sender: 'bot'
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const processMessage = async (text) => {
        if (!text.trim()) return;

        // Add user message to chat
        const userMessage = { id: Date.now(), text, sender: 'user' };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            // Send message to backend API
            const response = await sendMessage(text);
            
            // Generate audio for the response
            let audioUrl = null;
            try {
                audioUrl = await convertTextToSpeech(response.ai_explanation);
            } catch (voiceError) {
                console.error('Error generating voice response:', voiceError);
            }

            // Add bot response to chat
            setMessages(prev => [
                ...prev,
                {
                    id: Date.now() + 1,
                    text: response.ai_explanation,
                    sender: 'bot',
                    weatherData: response.weather_data,
                    audioUrl
                }
            ]);
        } catch (error) {
            console.error('Error sending message:', error);
            setMessages(prev => [
                ...prev,
                {
                    id: Date.now() + 1,
                    text: "Sorry, I couldn't process your request. Please try again.",
                    sender: 'bot',
                    error: true
                }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSend = () => {
        processMessage(input);
    };

    const handleVoiceRecording = async (audioBlob) => {
        try {
            const transcribedText = await convertSpeechToText(audioBlob);
            if (transcribedText) {
                setInput(transcribedText);
                await processMessage(transcribedText);
            }
        } catch (error) {
            console.error('Error processing voice recording:', error);
            setMessages(prev => [
                ...prev,
                {
                    id: Date.now() + 1,
                    text: "Sorry, I couldn't understand your voice message. Please try again or type your question.",
                    sender: 'bot',
                    error: true
                }
            ]);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <Paper
            elevation={3}
            sx={{
                height: '70vh',
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
                border: '1px solid rgba(0, 0, 0, 0.1)',
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)'
            }}
        >
            <Box sx={{ p: 2, borderBottom: '1px solid rgba(0, 0, 0, 0.1)' }}>
                <Typography variant="h6" sx={{ fontWeight: 500 }}>
                    Chat with Weather AI
                </Typography>
            </Box>

            <MessageList messages={messages} messagesEndRef={messagesEndRef} />

            <Box sx={{
                p: 2,
                borderTop: '1px solid rgba(0, 0, 0, 0.1)',
                display: 'flex',
                alignItems: 'center',
                backgroundColor: '#f9f9f9'
            }}>
                <TextField
                    fullWidth
                    variant="outlined"
                    placeholder="Ask about weather (e.g., What's the weather in London?)"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={isLoading}
                    size="small"
                    sx={{
                        mr: 1,
                        '& .MuiOutlinedInput-root': {
                            borderRadius: '20px',
                            backgroundColor: '#fff'
                        }
                    }}
                />
                
                <VoiceRecorder 
                    onRecordingComplete={handleVoiceRecording}
                    disabled={isLoading}
                />
                
                <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
                
                {isLoading ? (
                    <CircularProgress size={24} />
                ) : (
                    <IconButton
                        color="primary"
                        onClick={handleSend}
                        disabled={!input.trim()}
                        sx={{
                            backgroundColor: '#1976d2',
                            color: 'white',
                            '&:hover': {
                                backgroundColor: '#1565c0',
                            },
                            '&.Mui-disabled': {
                                backgroundColor: '#e0e0e0',
                                color: '#9e9e9e'
                            }
                        }}
                    >
                        <SendIcon />
                    </IconButton>
                )}
            </Box>
        </Paper>
    );
}

export default ChatInterface;