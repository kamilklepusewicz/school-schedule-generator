# Używamy lekkiej, oficjalnej wersji Pythona
FROM python:3.11-slim

# Blokujemy tworzenie plików .pyc i wymuszamy logowanie w czasie rzeczywistym
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Ustawiamy folder roboczy wewnątrz kontenera
WORKDIR /app

# Kopiujemy listę wymagań i instalujemy biblioteki
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy resztę kodu backendu do kontenera
COPY . .

# Uruchamiamy serwer uvicorn z opcją --reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]