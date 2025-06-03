FROM debian:bookworm

# Install Python, curl, and debugging tools
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
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN python3 -m venv /venv \
 && /venv/bin/pip install --upgrade pip \
 && /venv/bin/pip install flask requests

ENV PATH="/venv/bin:$PATH"

# Copy app
COPY app.py /app.py

# Start app
CMD ["python3", "/app.py"]
