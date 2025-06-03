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
RUN pip3 install flask requests

# Copy app
COPY app.py /app.py

# Start app
CMD ["python3", "/app.py"]
