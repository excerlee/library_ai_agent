#!/bin/bash
# Run the FastAPI application using uvicorn
# The --reload flag is useful for development but can be removed for production
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
