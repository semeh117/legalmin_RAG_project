# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install all libraries
RUN pip install --no-cache-dir -r requirements.txt

# Copy all frontend code
COPY . .

# Expose frontend port
EXPOSE 8501

# Start the frontend
CMD ["streamlit", "run", "app.py", "--server.port=8501"]