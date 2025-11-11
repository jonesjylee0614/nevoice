# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Architecture

E-Voice is a multi-service voice recognition and voiceprint identification system consisting of three main components:

### 1. e-voice (Python Backend)
Flask-based voice recognition service integrating FunASR and ModelScope models.
- **Port**: 8210 (configurable via `PORT` environment variable)
- **Entry**: `nevoice/e-voice/rest.py`
- **Tech Stack**: Flask, SocketIO, FunASR, ModelScope, PyTorch, Elasticsearch

### 2. e-voice-admin (Go Gateway)
Gin-based API gateway and business management backend.
- **Port**: 8108
- **Entry**: `nevoice/e-voice-admin/main.go`
- **Tech Stack**: Go 1.23+, Gin, GORM, PostgreSQL

### 3. e-voice-admin-front (Vue Frontend)
Management interface for voiceprint and meeting management.
- **Tech Stack**: Vue3, Vite, Arco Design, TypeScript
- **Entry**: `nevoice/e-voice-admin-front/src/main.ts`

## Running the Services

### Python Backend (e-voice)
```bash
cd nevoice/e-voice

# Set environment (dev/prod/test)
export EVOICE_ENV=dev

# Install dependencies
pip install -r requirements.txt

# Run server
python rest.py
# Server runs on http://0.0.0.0:8210
```

**Environment Configuration**:
- Set `EVOICE_ENV` to choose config: `dev`, `prod`, `test`
- Config files in `config/config.py`

### Go Gateway (e-voice-admin)
```bash
cd nevoice/e-voice-admin

# Default config (resource/config.yml)
go run main.go

# Specify environment (-e flag loads resource/config-{env}.yml)
go run main.go -e prod

# Custom config path
go run main.go -c ./path/to/config.yml

# Build
go build -o main main.go
```

### Vue Frontend (e-voice-admin-front)
```bash
cd nevoice/e-voice-admin-front

# Install dependencies
pnpm install

# Development server (proxies to port 8108)
pnpm run dev

# Build for production
pnpm run build
```

**Environment Variables**:
- `.env.development` - local dev settings
- `.env.production` - production settings
- Configure `VITE_API_HOST` and `VITE_API_PY_WS_HOST`

## Testing

### Python Backend Tests
Located in `nevoice/e-voice/tests/`:

```bash
cd nevoice/e-voice

# Run specific test
python tests/test_session_pipeline.py
python tests/websocket/test_streaming_basic.py

# Performance tests
python tests/performance_test.py
```

**HTML Test Pages**: Interactive test pages in `nevoice/e-voice/tests/`:
- Open `test_page.html` in browser for main test UI
- `pages/voice-test.html` - voiceprint registration tests
- `pages/speech-recognition-test.html` - ASR tests
- `pages/realtime-correction-demo.html` - streaming recognition with correction

### Go Backend Tests
```bash
cd nevoice/e-voice-admin

# Run all tests
go test ./...

# Test specific package
go test ./internal/app/voice/...
```

### Frontend Tests
```bash
cd nevoice/e-voice-admin-front

# Lint
pnpm run lint

# Type check
pnpm run type:check
```

## Key Technical Details

### Python Backend Architecture

**Critical Path Rule**: ALWAYS use relative paths, NEVER absolute paths like `/data/...`
- Correct: `data/voice/print/{userid}/`
- Wrong: `/data/voice/print/{userid}/` (causes WSL permission issues)

**Application Factory Pattern**: `nevoice/e-voice/server/app.py:create_app()`
- Registers Flask blueprints
- Initializes SocketIO and WebSocket routes
- Sets up CORS and logging

**Speech Recognition Models**:
- **ASR**: ModelScope `iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch`
  - Location: `speech_recognition/recognize.py`
  - Fallback: FunASR `paraformer-zh-streaming` for streaming
- **Voiceprint**: ModelScope `speech_campplus_sv_zh-cn_16k-common`
  - Location: `pipeline/spk_v_pipeline.py`, `speech_recognition/spk.py`

**WebSocket Real-time Recognition**: `/ws/recognize` endpoint
- Handler: `nevoice/e-voice/server/routes/ws.py`
- Session management: `nevoice/e-voice/server/session.py:RealtimeSpeechSession`
- Supports PCM/WebM audio frames via Base64 JSON packets
- Returns partial/final recognition results

**Logging System**: `nevoice/e-voice/server/logging.py`
- Multiple log files: `ws.log`, `audio.log`, `recognition_results.log`
- Uses Loguru for structured logging
- System monitoring: `monitoring/system_monitor.py` (CPU/GPU/latency tracking)

**Vector Database**: Elasticsearch 8.x for voiceprint storage
- Module: `nevoice/e-voice/es/voice.py`
- Index: `voice_print` with dense vector fields

### Go Backend Architecture

**Configuration**: `nevoice/e-voice-admin/resource/config.yml`
- Database config (PostgreSQL/MySQL via GORM)
- Microservice addresses (Python backend at `py_voice.host`)
- JWT, CORS, logging settings

**Key Modules**:
- `internal/app/voice/` - voiceprint management and gateway routing
- `internal/app/meeting/` - offline meeting processing APIs
- `internal/domain/` - DTOs and service interfaces
- `internal/model/` - GORM database models

**API Gateway Pattern**: Go service proxies requests to Python backend
- Example: `internal/app/voice/print.go` forwards to Python `/voice-register`
- Returns WebSocket addresses for real-time recognition

**Error Handling**: Global panic recovery middleware at `internal/route/middleware/error.go`

### Frontend Architecture

**Routing**: `src/router/index.ts`
- Uses `createWebHashHistory` for hash-based routing
- Routes defined in `src/router/routes/`

**State Management**: Pinia stores in `src/stores/`

**Key Views**:
- `src/views/voice/print/` - voiceprint management UI
  - `RealtimeForm.vue` - real-time recognition modal
  - `api/index.ts` - API integration
- `src/views/meeting/offline/` - meeting management
  - `AudioUpload.vue` - audio file upload component

**HTTP Client**: `src/utils/http/index.ts` - Axios wrapper with interceptors

**Environment Configuration**: Vite proxy in `vite.config.ts` routes `/api` to port 8108

## Core Data Flows

### Voiceprint Registration Flow
1. Frontend uploads audio via `src/views/voice/print/api/index.ts:saveUserPrint()`
2. Go gateway receives at `internal/app/voice/print.go:SaveUserPrint()`
3. Go proxies multipart request to Python `/voice-register`
4. Python extracts voiceprint embedding and stores in Elasticsearch
5. Returns text summary, duration, and embedding info

### Real-time Speech Recognition Flow
1. Frontend requests WebSocket address from Go gateway `/voice/gateway/wsRecognize/`
2. Go returns Python WS URL from config
3. Frontend connects to Python `/ws/recognize` and sends audio frames
4. Python `RealtimeSpeechSession` processes audio, performs VAD and recognition
5. Returns `partial` (intermediate) and `final` (confirmed) results as JSON
6. Logs raw audio and statistics for monitoring

### Offline Meeting Processing Flow
1. Frontend uploads meeting audio via `src/views/meeting/offline/AudioUpload.vue`
2. Go saves meeting metadata to database
3. Go forwards audio to Python `/meeting/offline/`
4. Python asynchronously processes with `biz/meeting/parse_offline_meeting.py`:
   - Runs FunASR speaker diarization
   - Extracts per-speaker segments
   - Matches voiceprints from Elasticsearch
   - Saves segments to database
5. Returns task status to frontend

## Development Conventions

### Python Code Style
- Use relative paths for all file operations
- Always include detailed error handling with traceback:
  ```python
  try:
      # business logic
      pass
  except Exception as e:
      print(f"Error: {traceback.format_exc()}")
      return {'error': str(e)}, 500
  ```
- Clear GPU memory with `torch.cuda.empty_cache()` after model inference
- Audio storage pattern: `data/voice/print/{userid}/{timestamp}.{uuid}.{filename}`

### Go Code Style
- Use panic for business errors - global middleware catches them
- Follow DTO pattern: request → domain service → model → database
- Add `recover()` in goroutines and scheduled tasks

### Frontend Code Style
- Use TypeScript for type safety
- API calls should use the centralized HTTP client
- Follow Arco Design component patterns

## Dependencies

### Python (requirements.txt)
- Flask 3.1.1, flask-socketio 5.5.1
- FunASR 1.2.6, ModelScope 1.22.3
- PyTorch 2.7.1, torchaudio, torchvision
- Elasticsearch 8.12.1
- librosa 0.11.0, soundfile 0.13.1
- loguru 0.7.3

**System Requirements**: `libsox-dev sox` for audio processing

### Go (go.mod)
- Go 1.23+
- Gin web framework
- GORM for database ORM
- PostgreSQL/MySQL drivers

### Frontend (package.json)
- Vue 3.2.40
- Vite (using rolldown-vite)
- Arco Design Web Vue 2.57.0
- Axios 1.11.0, Pinia 2.0.23
- socket.io-client 4.8.1 for WebSocket

## Common Issues

### ModelScope Model Loading Failures
- `recognize.py` catches exceptions and returns mock results
- Check logs in `logs/recognition_results.log`
- May need to re-download models or free GPU memory

### WebSocket Connection Issues
- Ensure frontend `.env` matches Go config `py_voice.host`
- Both must point to same Python service address
- CORS errors: check `allowurl` in `resource/config.yml`

### System Monitoring Not Starting
- Check `psutil` and `torch` are installed
- Enable monitoring in startup parameters
- Logs show "系统监控模块不可用" if dependencies missing

### Meeting Task Failures
- Check `parse_offline_meeting` logs
- Verify audio format compatibility
- Confirm Elasticsearch and database connectivity

## Documentation

Project documentation located in `nevoice/e-docs/`:
- `2025-项目指南/总体架构与说明.md` - comprehensive architecture guide
- `2025-项目指南/后端服务-e-voice详解.md` - Python backend details
- `2025-项目指南/网关服务-e-voice-admin详解.md` - Go gateway details
- `2025-项目指南/管理前端-e-voice-admin-front详解.md` - frontend details

Additional documentation:
- `nevoice/e-voice/tests/README.md` - testing guide
- `nevoice/e-voice/tests/TROUBLESHOOTING.md` - common error solutions
- `nevoice/e-voice/.cursor/rules/` - development guidelines and rules

## FunASR Subdirectory

The `FunASR/` directory contains the FunASR library source code for reference and potential customization. It is not directly used by the main application but provides model documentation and examples.
