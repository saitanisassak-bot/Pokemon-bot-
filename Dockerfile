# Python ka lightweight version use kar rahe hain
FROM python:3.11-slim

# App directory set kar rahe hain
WORKDIR /app

# Requirements file copy karke dependencies install karna
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baaki saari files (main.py, database.py, config.py) copy karna
COPY . .

# Bot ko start karne ka command
CMD ["python", "main.py"]
