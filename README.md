# Backend (FastAPI) + Postgres (Docker Compose)

1. Build and run
   docker compose up --build

   This will start:
   - Postgres on localhost:5432
   - Backend FastAPI on http://localhost:8000

2. Check health:
   - GET http://localhost:8000/docs  (OpenAPI / interactive docs)
   - GET http://localhost:8000/api/reviews  (should return an empty list initially)

3. Test webhook (manual)
   For now, you can simulate Twilio by POSTing form data:
   curl -X POST http://localhost:8000/webhook \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "From=whatsapp:+1234567890" \
     -d "Body=MyProduct"

   The endpoint returns TwiML XML. We'll connect Twilio sandbox and ngrok in the next step.
