# Crowd Sense Pro 🚶

**Real-Time Traffic & AI Analytics Edge Dashboard**

A cutting-edge AI-powered crowd detection and density analysis system with real-time WebSocket streaming, zone-based tracking, and SQLite analytics persistence.

## Features ✨

- **Real-Time Detection**: YOLO v8 object detection with ~30 FPS streaming
- **Crowd Density Analysis**: Multi-level density classification (LOW, MEDIUM, HIGH, CRITICAL)
- **Zone Tracking**: Dual-zone detection with centroid-based object tracking
- **Tripwire Monitoring**: Entry/exit counting across a virtual tripwire
- **Live Video Feed**: Base64-encoded frame streaming via WebSocket
- **Analytics Persistence**: SQLite database for historical trend analysis
- **Modern Dashboard**: React + Tailwind CSS with real-time charts and KPI tiles
- **Mock Mode**: Graceful fallback with synthetic data when YOLO is unavailable

## Architecture 🏗️

```
crowdsense-pro/
├── backend/                 # FastAPI server
│   ├── main.py             # WebSocket & REST endpoints
│   ├── detector.py         # YOLO + centroid tracker
│   ├── analytics.py        # Density computation
│   ├── database.py         # SQLAlchemy ORM
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React Vite app
│   ├── src/
│   │   ├── App.jsx        # Main dashboard
│   │   ├── components/    # KPI tiles, charts
│   │   └── hooks/         # WebSocket hook
│   ├── package.json
│   └── vite.config.js
├── data/
│   ├── sample_videos/     # Test video files
│   └── crowdsense.db      # SQLite database
├── models/                # YOLO weights
└── docker-compose.yml     # Full stack orchestration
```

## Quick Start 🚀

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/crowdsense-pro.git
cd crowdsense-pro

# Backend setup
cd backend
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Running the System

#### Option 1: Docker (Recommended)
```bash
docker-compose up
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

#### Option 2: Manual Development

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Opens http://localhost:5173
```

## API Endpoints 📡

### WebSocket
- **`ws://localhost:8000/ws/analytics`** - Real-time frame & metrics streaming
  - Sends: `{ frame, total_people, density_level, zone_a, zone_b, crossed_in, crossed_out, alert?, message? }`
  - ~30 FPS frame rate

### REST API
- **`GET /api/history?limit=200`** - Historical analytics records
  - Response: `[{ timestamp, total_people, density_level }, ...]`

## Configuration 🔧

### Video Source
Modify in `backend/main.py`:
```python
cap = cv2.VideoCapture(0)           # Webcam (0)
cap = cv2.VideoCapture('video.mp4') # Video file
```

### Detection Thresholds
Adjust in `backend/analytics.py`:
```python
DENSITY_THRESHOLDS = {
    'low': 5,      # < 5 people = LOW
    'medium': 15,  # 5-14 = MEDIUM
    'high': 30,    # 15-29 = HIGH
    # >= 30 = CRITICAL
}
```

### Zone & Tripwire
Configure in `backend/detector.py`:
```python
ZONE_A = np.array([[10, 150], [310, 150], [310, 470], [10, 470]])
ZONE_B = np.array([[330, 150], [630, 150], [630, 470], [330, 470]])
TRIPWIRE_Y = 300
```

## Dashboard Metrics 📊

| Metric | Description |
|--------|------------|
| **Live People** | Current person count |
| **Live Vehicles** | Current vehicle count |
| **Density Level** | Classification based on thresholds |
| **Danger Score** | 0-100 risk metric |
| **Zone A/B** | Objects in each detection zone |
| **Tripwire IN/OUT** | Cumulative crossing counts |

## Database Schema 🗄️

```sql
CREATE TABLE analytics (
    id INTEGER PRIMARY KEY,
    timestamp FLOAT,
    total_people INTEGER,
    total_vehicles INTEGER,
    density_level STRING,
    density_score INTEGER
);
```

Records saved every 30 frames (~1 second at 30 FPS).

## Performance 📈

- **Detection**: ~30 FPS on GPU, ~10 FPS on CPU
- **Frame Size**: 640x480 (reduced to 70% JPEG quality for bandwidth)
- **Network**: ~500 KB/s per client at 30 FPS
- **Database**: Async SQLite with session-based commits

## Troubleshooting 🔨

### PyTorch DLL Error
```
Error loading "torch\lib\c10.dll"
```
**Solution**: System runs in MOCK mode with synthetic data. Install correct PyTorch wheel:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### WebSocket Connection Failed
- Ensure backend is running on `http://localhost:8000`
- Check CORS middleware in `backend/main.py`
- Verify firewall allows port 8000

### No Video Stream
- Check video file path in `backend/main.py`
- Verify webcam permissions (Windows/Linux)
- Try webcam fallback: `cv2.VideoCapture(0)`

## Tech Stack 🛠️

**Backend:**
- FastAPI - Async web framework
- Uvicorn - ASGI server
- Ultralytics YOLOv8 - Object detection
- SQLAlchemy - ORM
- OpenCV - Video processing
- WebSockets - Real-time streaming

**Frontend:**
- React 19 - UI framework
- Vite 8 - Build tool
- Tailwind CSS 4 - Styling
- Recharts - Chart visualization
- Lucide React - Icons

## Future Enhancements 🚀

- [ ] Multi-zone heatmaps
- [ ] Anomaly detection alerts
- [ ] Person re-identification (ReID)
- [ ] Edge deployment (NVIDIA Jetson)
- [ ] Kubernetes orchestration
- [ ] GraphQL API
- [ ] Mobile companion app
- [ ] Historical data export (CSV/PDF)

## Contributing 🤝

Pull requests welcome! Please follow:
1. Fork the repo
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

MIT License - see [LICENSE](LICENSE) file for details

## Author 👤

**Sunil Choubey**
- GitHub: [@sunilchoubey](https://github.com/sunilchoubey)

## Support 💬

For issues and questions, please open an [Issue](https://github.com/yourusername/crowdsense-pro/issues).

---

**Made with ❤️ for smarter crowd management**
