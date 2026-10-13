FROM python:3.13-slim

WORKDIR /app

# Kutubxonalarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini ko'chirish
COPY . .

# Server porti (Render yoki Koyeb uchun)
ENV PORT=8080
EXPOSE 8080

CMD ["python", "main.py"]
