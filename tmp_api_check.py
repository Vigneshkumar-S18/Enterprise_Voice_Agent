from fastapi.testclient import TestClient
from src.voxops.backend.main import app

client = TestClient(app)

checks = []

def run():
    r = client.get('/')
    checks.append(('GET /', r.status_code, r.json()))

    r = client.get('/health')
    checks.append(('GET /health', r.status_code, r.json()))

    r = client.get('/orders/')
    checks.append(('GET /orders/', r.status_code, len(r.json())))

    r = client.get('/orders/ORD-001')
    checks.append(('GET /orders/ORD-001', r.status_code, r.json().get('order_id')))

    r = client.get('/simulation/predict-delivery/ORD-001')
    checks.append(('GET /simulation/predict-delivery/ORD-001', r.status_code, r.json().get('estimated_hours')))

    # create ticket
    payload = {
        'customer_id': 'CUST-TEST',
        'issue_summary': 'Test issue',
        'transcript': 'Test transcript',
        'order_id': 'ORD-001',
        'priority': 'normal',
    }
    r = client.post('/agent/create-ticket', json=payload)
    checks.append(('POST /agent/create-ticket', r.status_code, r.json().get('ticket_id')))

    r = client.get('/agent/tickets')
    checks.append(('GET /agent/tickets', r.status_code, len(r.json())))

    r = client.post('/voice/voice-query', data={'text': 'Status of ORD-001 please'})
    checks.append(('POST /voice/voice-query', r.status_code, r.json().get('transcript')))

    for name, status, detail in checks:
        print(f"{name}: status={status} -> {detail}")

if __name__ == '__main__':
    run()
