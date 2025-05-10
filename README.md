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
cd "d:\ProjectFolder\Weather AI Agent\Frontend"
```
2. Install the required packages.
```bash
npm install
```
3. Create a .env file with your ElevenLabs API key:
VITE_ELEVENLABS_API_KEY=your_elevenlabs_api_key

4. Start the frontend server.
```bash
npm run dev
```
The frontend will be available at http://localhost:5173