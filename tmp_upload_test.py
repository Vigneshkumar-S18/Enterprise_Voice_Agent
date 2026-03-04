from fastapi.testclient import TestClient
from src.voxops.backend.main import app
from pathlib import Path

client = TestClient(app)

wav = Path('test_audio.wav')
if not wav.exists():
    raise SystemExit('test_audio.wav not found')

with wav.open('rb') as fh:
    files = {'audio': (wav.name, fh, 'audio/wav')}
    resp = client.post('/voice/voice-query', files=files)

print('status:', resp.status_code)
try:
    print('json:', resp.json())
except Exception:
    print('text:', resp.text)
