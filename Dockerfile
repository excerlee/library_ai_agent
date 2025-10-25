# Use the official Playwright image with Python, which includes all necessary system dependencies for the browsers
FROM mcr.microsoft.com/playwright/python:latest

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the FastAPI application runs on
EXPOSE 8000

# Command to run the application using uvicorn
# The run.sh script already uses uvicorn, so we'll just execute it.
CMD ["./run.sh"]
