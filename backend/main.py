import asyncio, json, base64, cv2
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from detector import ObjectDetector
from analytics import compute_density
from database import save_record, get_recent

app = FastAPI(title='Crowd Sense Pro API')
app.add_middleware(CORSMiddleware, allow_origins=['*'],
                   allow_methods=['*'], allow_headers=['*'])

detector = ObjectDetector()
clients: set[WebSocket] = set()
frame_count = 0

@app.websocket('/ws/analytics')
async def analytics_ws(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True: await asyncio.sleep(1)   # keep alive
    except WebSocketDisconnect:
        clients.discard(ws)

async def broadcast(payload: dict):
    global clients
    dead = set()
    for ws in clients:
        try:    await ws.send_json(payload)
        except: dead.add(ws)
    clients -= dead

@app.on_event('startup')
async def start_video_loop():
    asyncio.create_task(video_loop())

async def video_loop():
    global frame_count
    # Change to sample video file instead of webcam
    cap = cv2.VideoCapture('../data/sample_videos/traffic.mp4')
    
    # If video file fails, try to fallback to webcam
    if not cap.isOpened():
        print("Warning: Cannot open video file. Falling back to webcam 0.")
        cap = cv2.VideoCapture(0)
        
    while True:
        ret, frame = cap.read()
        if not ret: 
            # If video ends (e.g. file), loop it
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
            
        result   = detector.detect(frame)
        metrics  = compute_density(result['counts'])
        _, buf   = cv2.imencode('.jpg', result['frame'], [cv2.IMWRITE_JPEG_QUALITY, 70])
        b64frame = base64.b64encode(buf).decode()
        
        payload = {
            **metrics, 
            'frame': b64frame,
            'zone_a': result['zone_a'],
            'zone_b': result['zone_b'],
            'crossed_in': result['in'],
            'crossed_out': result['out']
        }
        
        # Alert system
        if metrics['density_level'] == 'CRITICAL':
            payload['alert'] = 'CRITICAL_DENSITY'
            payload['message'] = f"{metrics['total_people']} people detected!"
            
        await broadcast(payload)
        
        frame_count += 1
        if frame_count % 30 == 0:
            save_record(metrics)
            
        await asyncio.sleep(0.033)      # ~30 fps
        
@app.get('/api/history')
def history(limit: int = 200):
    return get_recent(limit)
