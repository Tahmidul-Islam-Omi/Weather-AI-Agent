
// Use the API key that we know works from the curl command
const API_KEY = 'sk_1d010d5b15299cb7e58d2f0f6d27dd63ad6277cf02a3f801';
const VOICE_ID = 'EXAVITQu4vr4xnSDxMaL'; // Default voice ID

// Text-to-Speech: Convert text to audio
export const convertTextToSpeech = async (text) => {
    try {
        console.log('Starting text-to-speech conversion...');
        
        // Log full request details for debugging
        const requestBody = {
            text,
            model_id: 'eleven_monolingual_v1',
            voice_settings: {
                stability: 0.5,
                similarity_boost: 0.5,
            }
        };
        
        console.log('Request URL:', `https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}`);
        console.log('Request headers:', { 'xi-api-key': API_KEY.substring(0, 5) + '...' });
        console.log('Request body:', JSON.stringify(requestBody));
        
        // Try using fetch instead of axios as an alternative approach
        const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}`, {
            method: 'POST',
            headers: {
                'xi-api-key': API_KEY,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('ElevenLabs API error:', {
                status: response.status,
                statusText: response.statusText,
                errorText
            });
            
            if (response.status === 401) {
                throw new Error(`ElevenLabs API authentication failed (${response.status}): ${response.statusText}`);
            }
            
            throw new Error(`ElevenLabs API request failed (${response.status}): ${response.statusText}`);
        }
        
        console.log('Successfully received audio response');
        const audioBuffer = await response.arrayBuffer();
        const audioBlob = new Blob([audioBuffer], { type: 'audio/mpeg' });
        return URL.createObjectURL(audioBlob);
    } catch (error) {
        console.error('Detailed error in convertTextToSpeech:', error);
        // Provide a more useful error message to the UI
        if (error.message.includes('authentication failed')) {
            throw new Error('Voice service authentication failed. API key may be valid but another issue is preventing access.');
        }
        throw error;
    }
};

// Speech-to-Text: Convert audio to text
export const convertSpeechToText = async (audioBlob) => {
    try {
        console.log('Starting speech-to-text conversion...');
        
        // Create form data with the original audio blob
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.webm');
        formData.append('model_id', 'scribe_v1');
        
        console.log('Request URL: https://api.elevenlabs.io/v1/speech-to-text');
        console.log('Request headers:', { 'xi-api-key': API_KEY.substring(0, 5) + '...' });
        
        // Try using fetch instead of axios
        const response = await fetch('https://api.elevenlabs.io/v1/speech-to-text', {
            method: 'POST',
            headers: {
                'xi-api-key': API_KEY,
                // No Content-Type header here - fetch will set it with the boundary
            },
            body: formData
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('ElevenLabs API error:', {
                status: response.status,
                statusText: response.statusText,
                errorText
            });
            
            if (response.status === 401) {
                throw new Error(`ElevenLabs API authentication failed (${response.status}): ${response.statusText}`);
            }
            
            throw new Error(`ElevenLabs API request failed (${response.status}): ${response.statusText}`);
        }
        
        const responseData = await response.json();
        console.log('Transcription response:', responseData);
        
        if (responseData && responseData.text) {
            return responseData.text;
        } else {
            throw new Error('No transcription text returned');
        }
    } catch (error) {
        console.error('Detailed error in convertSpeechToText:', error);
        
        // Provide a more useful error message to the UI
        if (error.message.includes('authentication failed')) {
            throw new Error('Voice service authentication failed. API key may be valid but another issue is preventing access.');
        }
        
        throw error;
    }
};