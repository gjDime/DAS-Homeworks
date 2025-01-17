# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app
# Copy the current directory contents into the container at /app
COPY . /app
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#Expose default port for the Flask application is 5000.
EXPOSE 5000

# Define the command to run the application
CMD ["python", "calc.py"]
