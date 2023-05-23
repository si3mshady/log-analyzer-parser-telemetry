# Base image
FROM python:3.9-slim


RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*


# Set the working directory
WORKDIR /app

# Copy the application files to the container
COPY app.py requirements.txt /app/

RUN /usr/local/bin/python -m pip install --upgrade pip

# Install the dependencies
RUN pip3 install -r requirements.txt

# Expose the port for Streamlit
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "--server.port", "8501", "--server.enableCORS", "false", "app.py"]
