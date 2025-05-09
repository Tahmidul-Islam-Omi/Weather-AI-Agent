import axios from 'axios';

const API_KEY = import.meta.env.VITE_ELEVENLABS_API_KEY || '';
const VOICE_ID = 'EXAVITQu4vr4xnSDxMaL'; // Default voice ID

// Speech-to-Text: Convert audio to text
export const convertSpeechToText = async (audioBlob) => {
    try {
        // Create form data with the original audio blob
        const formData = new FormData();
        
        // Use the original blob format (webm) instead of trying to convert it
        formData.append('file', audioBlob, 'recording.webm');
        formData.append('model_id', 'eleven_multilingual_v2');

        console.log('Sending audio for transcription...');

        const response = await axios.post(
            'https://api.elevenlabs.io/v1/speech-to-text',
            formData,
            {
                headers: {
                    'xi-api-key': API_KEY,
                    'Content-Type': 'multipart/form-data',
                },
                timeout: 30000 // 30-second timeout
            }
        );

        console.log('Transcription response:', response.data);

        if (response.data && response.data.text) {
            return response.data.text;
        } else {
            throw new Error('No transcription text returned');
        }
    } catch (error) {
        console.error('Error converting speech to text:', error);
        if (error.response) {
            console.error('API error details:', error.response.data);
            
            // If we get a specific error about format, try again with a different format
            if (error.response.status === 400) {
                try {
                    console.log('Retrying with alternative format...');
                    // Try converting to MP3 (if browser supports it) or WAV as fallback
                    const reader = new FileReader();
                    reader.readAsArrayBuffer(audioBlob);
                    
                    const audioArrayBuffer = await new Promise((resolve, reject) => {
                        reader.onload = () => resolve(reader.result);
                        reader.onerror = reject;
                    });
                    
                    // Just try with the original buffer data but different extension
                    const altFormData = new FormData();
                    const altBlob = new Blob([audioArrayBuffer], { type: 'audio/mp3' });
                    altFormData.append('file', altBlob, 'recording.mp3');
                    altFormData.append('model_id', 'eleven_multilingual_v2');
                    
                    const altResponse = await axios.post(
                        'https://api.elevenlabs.io/v1/speech-to-text',
                        altFormData,
                        {
                            headers: {
                                'xi-api-key': API_KEY,
                                'Content-Type': 'multipart/form-data',
                            },
                            timeout: 30000
                        }
                    );
                    
                    if (altResponse.data && altResponse.data.text) {
                        return altResponse.data.text;
                    }
                } catch (fallbackError) {
                    console.error('Fallback transcription also failed:', fallbackError);
                }
            }
        }
        throw error;
    }
};

// Text-to-Speech: Convert text to audio
export const convertTextToSpeech = async (text) => {
    try {
        const response = await axios.post(
            `https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}`,
            {
                text,
                model_id: 'eleven_monolingual_v1',
                voice_settings: {
                    stability: 0.5,
                    similarity_boost: 0.5,
                },
            },
            {
                headers: {
                    'xi-api-key': API_KEY,
                    'Content-Type': 'application/json',
                },
                responseType: 'arraybuffer',
            }
        );

        // Convert the array buffer to an audio blob
        const audioBlob = new Blob([response.data], { type: 'audio/mpeg' });
        return URL.createObjectURL(audioBlob);
    } catch (error) {
        console.error('Error converting text to speech:', error);
        throw error;
    }
};