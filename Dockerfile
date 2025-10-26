from balenalib/rpi-raspbian:bullseye

run apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

workdir /samsim

run python3 -m venv /opt/venv
env PATH="/opt/venv/bin:$PATH"

copy requirements.txt .

run pip3 install --upgrade pip
run pip3 install --no-cache-dir -r requirements.txt

copy . .

env PYTHONUNBUFFERED=1
expose 5000

cmd ["gunicorn", "--bind=0.0.0.0:5000", "--workers=1", "--worker-class=sync", "wsgi:application"]
