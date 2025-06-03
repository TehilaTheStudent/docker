FROM debian:bookworm

# Install curl, networking/system tools, and Python 3
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

CMD ["bash"]
