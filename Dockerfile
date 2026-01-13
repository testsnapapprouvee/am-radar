# On part d'une version légère de Python
FROM python:3.9-slim

# 1. On installe Chromium et le Driver proprement via les paquets officiels Linux
# Plus de devinette, ils seront dans /usr/bin/
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    cron \
    && rm -rf /var/lib/apt/lists/*

# 2. On définit les variables d'environnement pour que Python les trouve
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PYTHONUNBUFFERED=1

# 3. On installe ton projet
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 4. On lance le script
CMD ["python", "main.py"]
