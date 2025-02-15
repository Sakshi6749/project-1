FROM python:3.12-slim-bookworm

# The installer requires curl (and certificates) to download the release archive

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    nodejs \
    npm \
    && npm install -g prettier@3.4.2 \
    && rm -rf /var/lib/apt/lists/*

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the PATH
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

COPY app.py /app/




RUN  pip install fastapi

RUN pip install unicorn

RUN pip install uvicorn

RUN pip install requests

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh


RUN mkdir -p /data

#COPY app_first.py /app
CMD ["uv", "run", "app.py"]

EXPOSE 8000