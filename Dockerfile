# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

# Command to run the app with live reload (for development)
# Use `--host 0.0.0.0` to be accessible outside the container
CMD ["uvicorn", "Routes:app", "--host", "0.0.0.0", "--port", "8000"]
