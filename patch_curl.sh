curl -X PATCH "http://127.0.0.1:8000/employee/1" \
     -H "Content-Type: application/json" \
     -d '{"email": "new.email@example.com"}'