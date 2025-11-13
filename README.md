# Lightning Triage™

AI-Powered Emergency Department Management System using Microsoft Agent Lightning

## Architecture

This is a **hybrid Rust + Python system** with 7 AI agents orchestrated through Azure OpenAI:

- **Rust Actix-web Backend** (port 8000): Main API, SQLite database, WebSocket server
- **Python FastAPI Inference Service** (port 8001): 6 AI agents using Azure OpenAI (O3, GPT-5, DeepSeek-V3)
- **React TypeScript Frontend** (port 5173): Dark theme dashboard with real-time updates

## Mission Statement

ContosoHealth is a faith-based healthcare organization dedicated to providing compassionate, AI-enhanced emergency care that honors the dignity of every patient. Our mission is to combine cutting-edge technology with faith-driven values to deliver exceptional emergency department management.

## Features

✅ **Faker-Generated Patient Data**: Realistic synthetic patient names, complaints, and vitals  
✅ **16-Bed Grid**: Color-coded by ESI level (1-5) with live status updates  
✅ **Scrolling AI Alerts**: Auto-updating recommendations from 7 AI agents  
✅ **Request Bed Modal**: AI-powered bed assignment requests  
✅ **7 AI Agents**: Coordinator, Triage, Resource Prediction, Bed Assignment, Staffing, Wait Time, Clinical Deterioration  
✅ **Real-Time WebSocket**: Live dashboard updates  
✅ **Metrics Dashboard**: Door-to-provider time, LWBS rate, bed utilization, patient satisfaction

## Quick Start

### 1. Start Rust Backend
```bash
cd rust-backend
cargo run
# Runs on http://localhost:8000
```

### 2. Start Python Inference Service
```bash
cd python-inference
poetry install
poetry run fastapi dev app/main.py
# Runs on http://localhost:8001
```

### 3. Start React Frontend
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

## Environment Variables

See `.env` files in each service directory for Azure OpenAI credentials and configuration.

## Technology Stack

- **Backend**: Rust 1.91+, Actix-web 4.9, SQLite, tokio
- **Inference**: Python 3.12, FastAPI, Azure OpenAI SDK, Pydantic
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Faker.js
- **AI Models**: Azure OpenAI GPT-5, O3, DeepSeek-V3

## Agent Lightning Integration

The system is designed to integrate with Microsoft Agent Lightning for agent training and optimization (feature-flagged for future implementation).

## License

MIT
