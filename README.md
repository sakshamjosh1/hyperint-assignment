# Hyperint Assignment — WhatsApp Product Review Collector

A minimal full-stack project that collects product reviews via a WhatsApp conversation, stores them in PostgreSQL, and displays them in a clean React dashboard.

This assignment includes:

- FastAPI backend  
- React + Vite frontend  
- PostgreSQL database  
- Docker Compose setup  
- Optional Twilio Sandbox integration  
- Local testing using curl (no Twilio required)

---

## 🚀 Features

- Multi-step WhatsApp workflow: **Product → Name → Review**
- Data stored in **PostgreSQL**
- **REST API** to fetch all reviews
- **React dashboard** to display submitted reviews
- **Dockerized** backend & database
- **CORS-enabled** backend
- Full **local simulation** using `curl`
- Optional **Twilio Sandbox** using ngrok

---

## 📂 Project Structure

```
hyperint-assignment/
│
├── app/
│   ├── main.py              # FastAPI backend
│   ├── __pycache__/
│   └── .env.example         # Backend environment variables
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── config.js
│   │   ├── styles.css
│   │   ├── components/
│   │   └── index.jsx
│   ├── vite.config.js
│   ├── package.json
│   └── .env.example
│
├── docker-compose.yml
├── Dockerfile               # Backend Dockerfile
├── requirements.txt
└── README.md                # This file
```

---

## 🐳 Running the Project (Docker)

From the root directory:

```bash
docker compose up --build
```

Services started:

- **Backend:** http://localhost:8000  
- **Frontend (after you run it manually):** http://localhost:5173  
- **PostgreSQL:** localhost:5432  

Backend API:

| Method | Path          | Description           |
|--------|---------------|-----------------------|
| POST   | /webhook      | Twilio WhatsApp hook  |
| GET    | /api/reviews  | Fetch all reviews     |

---

## 💻 Running the Frontend (React + Vite)

```
cd frontend
npm install
npm run dev
```

Frontend available at:

```
http://localhost:5173/
```

---

## 🧪 Local Testing (NO Twilio Required)

Simulate a complete WhatsApp conversation using curl:

### 1️⃣ Send product name
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+14155551212" \
  -d "Body=Macbook Air M3"
```

### 2️⃣ Send user name
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+14155551212" \
  -d "Body=Saksham"
```

### 3️⃣ Send review
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+14155551212" \
  -d "Body=Amazing product, super lightweight!"
```

### 🔍 Check database
```bash
docker compose exec db psql -U postgres -d reviewsdb \
  -c "SELECT * FROM reviews ORDER BY created_at DESC LIMIT 20;"
```

---

## 📱 Optional: Twilio Sandbox (WhatsApp)

You can enable actual WhatsApp messaging.

### 1️⃣ Start ngrok

```bash
ngrok http 8000
```

Copy the HTTPS URL:

```
https://xxxxx.ngrok-free.app/webhook
```

### 2️⃣ Configure in Twilio

Go to:

```
Twilio Console → Messaging → WhatsApp Sandbox
```

Set webhook:

```
WHEN A MESSAGE COMES IN → https://xxxxx.ngrok-free.app/webhook
```

### 3️⃣ Send a WhatsApp message to your sandbox number  
The backend will respond automatically.

---

## 🔧 Environment Variables

### **Backend → app/.env.example**
```
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=reviewsdb
DB_CONNECT_RETRIES=15
DB_CONNECT_DELAY=1
DB_CONNECT_TIMEOUT=30
```

### **Frontend → frontend/.env.example**
```
VITE_API_URL=http://localhost:8000
```

---

## 👤 Author

**Saksham Joshi**  
GitHub: https://github.com/sakshamjosh1/hyperint-assignment  

Project built as part of **Hyperint Software Developer Engineer Assignment**.
