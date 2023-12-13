# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory files (on your machine) to the container
ADD . /app/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -e .

# Expose the port Streamlit app is running on
EXPOSE 8501

# Run app
ENTRYPOINT ["streamlit", "run", "plclient/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
