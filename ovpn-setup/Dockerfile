# Use an official Ubuntu image as the base
FROM debian

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    software-properties-common \
    python3 \
    python3-pip \
    openvpn \
    easy-rsa \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the Python dependencies
RUN pip3 install --upgrade pip --break-system-packages
COPY requirements.txt /app/
RUN pip3 install -r  requirements.txt --break-system-packages
# Expose the port the app runs on
EXPOSE 4000

# Command to run the application
CMD ["python3", "app.py"]

