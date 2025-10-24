FROM nvidia/cuda:12.6.0-cudnn-devel-ubuntu22.04

LABEL maintainer="XXXXRT"
LABEL version="V5"
LABEL description="Docker image for GPT-SoVITS without conda"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/workspace/GPT-SoVITS"

SHELL ["/bin/bash", "-c"]

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    ffmpeg \
    git \
    wget \
    curl \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Set python3.11 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

WORKDIR /workspace/GPT-SoVITS

# Copy and install requirements
COPY requirements.txt /workspace/GPT-SoVITS/
RUN pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cu126 && \
    pip install --no-cache-dir Cython && \
    pip install --no-cache-dir git+https://github.com/r9y9/pyopenjtalk.git@v0.4.1 && \
    sed -i '/pyopenjtalk/d' requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ /workspace/GPT-SoVITS/app/
COPY GPT_SoVITS/ /workspace/GPT-SoVITS/GPT_SoVITS/
COPY config/ /workspace/GPT-SoVITS/config/
COPY tools/ /workspace/GPT-SoVITS/tools/
COPY api/ /workspace/GPT-SoVITS/api/

EXPOSE 9871 9872 9873 9874 9880

CMD ["python", "app/webui.py"]