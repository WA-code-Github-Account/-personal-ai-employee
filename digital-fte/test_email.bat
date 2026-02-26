@echo off
powershell -Command "Invoke-WebRequest -Uri 'http://localhost:3000/call' -Method POST -ContentType 'application/json' -Body '{\"method\":\"send_email\",\"params\":{\"recipient\":\"wahishaikh545@gmail.com\",\"subject\":\"Test Email\",\"body\":\"Hello from AI Employee!\"}}'"
pause