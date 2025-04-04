# Python image 
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements 
COPY requirements.txt .

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy FastAPI application files 
COPY . .

# Run 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "17787"]

