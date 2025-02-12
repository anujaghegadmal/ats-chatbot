# Use official Python image
FROM python:3.10

# Set working directory inside container
WORKDIR /app

# Copy requirements file from root directory
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app directory into the container
COPY app /app/app

# Expose the port FastAPI runs on
EXPOSE 8000

# Run FastAPI using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
