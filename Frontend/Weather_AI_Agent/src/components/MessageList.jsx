import { Box, Typography, Paper, Avatar } from '@mui/material';
import CloudIcon from '@mui/icons-material/Cloud';
import PersonIcon from '@mui/icons-material/Person';
import WeatherDisplay from './WeatherDisplay';
import AudioPlayer from './AudioPlayer';

function MessageList({ messages, messagesEndRef }) {
    return (
        <Box
            sx={{
                flexGrow: 1,
                overflowY: 'auto',
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
                backgroundColor: '#f5f7fa'
            }}
        >
            {messages.map((message) => (
                <Box
                    key={message.id}
                    sx={{
                        display: 'flex',
                        flexDirection: 'row',
                        alignItems: 'flex-start',
                        justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                    }}
                >
                    {message.sender === 'bot' && (
                        <Avatar
                            sx={{
                                mr: 1,
                                bgcolor: 'primary.main',
                                width: 36,
                                height: 36
                            }}
                        >
                            <CloudIcon fontSize="small" />
                        </Avatar>
                    )}

                    <Paper
                        elevation={0}
                        sx={{
                            p: 2,
                            maxWidth: '80%',
                            borderRadius: message.sender === 'user' ? '20px 20px 4px 20px' : '20px 20px 20px 4px',
                            backgroundColor: message.sender === 'user' ? 'primary.main' : 'white',
                            color: message.sender === 'user' ? 'white' : 'text.primary',
                            border: message.sender === 'bot' ? '1px solid rgba(0, 0, 0, 0.1)' : 'none',
                            ...(message.error && { borderColor: '#f44336', borderWidth: 1 })
                        }}
                    >
                        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                            {message.text}
                        </Typography>
                        
                        {message.weatherData && <WeatherDisplay data={message.weatherData} />}
                        
                        {message.audioUrl && <AudioPlayer audioUrl={message.audioUrl} />}
                    </Paper>

                    {message.sender === 'user' && (
                        <Avatar
                            sx={{
                                ml: 1,
                                bgcolor: 'secondary.main',
                                width: 36,
                                height: 36
                            }}
                        >
                            <PersonIcon fontSize="small" />
                        </Avatar>
                    )}
                </Box>
            ))}
            <div ref={messagesEndRef} />
        </Box>
    );
}

export default MessageList;