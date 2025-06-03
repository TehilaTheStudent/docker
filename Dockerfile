FROM debian:bookworm

# Install base system tools, Python, and venv support
RUN apt-get update && apt-get install -y \
    curl \
    iputils-ping \
    dnsutils \
    net-tools \
    iproute2 \
    telnet \
    tcpdump \
    ca-certificates \
    vim \
    gnupg \
    lsof \
    traceroute \
    python3 \
    python3-pip \
    python3-venv \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a virtual environment and install Python packages
RUN python3 -m venv /venv \
 && /venv/bin/pip install --upgrade pip \
 && /venv/bin/pip install flask requests

# Use the venv by default
ENV PATH="/venv/bin:$PATH"

# Copy your app code
COPY app.py /app.py

# Start the app
CMD ["python3", "/app.py"]
