# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /reward-extractor

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY ./src src
COPY ./abi abi
COPY ./test test

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the command to run the application
CMD ["python", "src/extract_rewards.py"]