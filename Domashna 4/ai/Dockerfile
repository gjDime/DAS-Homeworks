FROM python:3.10

WORKDIR /app

# Copy only requirements.txt first to leverage Docker's caching mechanism
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application
COPY . .

# Expose the port for the FastAPI app
EXPOSE 8000

# Start the FastAPI app with Uvicorn
CMD ["uvicorn", "prediction_api:app", "--host", "0.0.0.0", "--port", "8000"]
