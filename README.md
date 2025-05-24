Backend Setup
1. Navigate to the backend directory.
```bash
cd "d:\ProjectFolder\Weather AI Agent\Backend"
```
2. Create a virtual environment.
```bash
python -m venv venv
```
3. Activate the virtual environment.
```bash
.\venv\Scripts\activate
```
4. Install the required packages.
```bash
pip install -r requirements.txt
```
5. Create a .env file and add the following variables.

6.Start the backend server.
```bash
uvicorn app.main:app --reload
```
The API will be available at http://localhost:8000 , and the API documentation at http://localhost:8000/docs .

Frontend Setup
1. Navigate to the frontend directory.
```bash
cd "d:\ProjectFolder\Weather AI Agent\Frontend\Weather_AI_Agent"
```
2. Install the required packages.
```bash
npm install
```
3. Create a .env file in the Weather_AI_Agent directory with your ElevenLabs API key:
```
VITE_ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

Note about ElevenLabs API:
- The app uses ElevenLabs for text-to-speech and speech-to-text functionality
- You need to sign up at https://elevenlabs.io/ to get an API key
- Free tier has limited usage, so you may need to upgrade for extended use
- If you encounter a 401 error, your API key may be expired or invalid
- Without a valid API key, voice features will be disabled but text chat will work normally

4. Start the frontend server.
```bash
npm run dev
```
The frontend will be available at http://localhost:5173