curl -v -X POST http://127.0.0.1:8000/login \
     -H "Content-Type: application/json" \
     -d '{"name": "Yannik", "email": "yannik.sacherer@google.de", "hashed_password": "blabliblub"}'