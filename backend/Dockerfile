# Use official Python lightweight image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code files
COPY backend/ ./backend/
COPY model/ ./model/
COPY data/ ./data/

# Switch to backend directory so imports resolve correctly
WORKDIR /app/backend

# Expose Flask port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
