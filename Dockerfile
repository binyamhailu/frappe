FROM python:3.11-slim-bookworm

ARG FRAPPE_BRANCH=version-15
ARG ERPNEXT_BRANCH=version-15

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    mariadb-client \
    libmariadb-dev \
    build-essential \
    python3-dev \
    redis-tools \
    xvfb \
    libfontconfig \
    wkhtmltopdf \
    cron \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install yarn
RUN npm install -g yarn

# Create frappe user
RUN useradd -m -s /bin/bash frappe \
    && echo "frappe ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER frappe
WORKDIR /home/frappe

# Install frappe-bench
RUN pip install --user frappe-bench

ENV PATH="/home/frappe/.local/bin:${PATH}"

# Initialize bench
RUN bench init frappe-bench \
    --frappe-branch ${FRAPPE_BRANCH} \
    --skip-redis-config-generation \
    --verbose

WORKDIR /home/frappe/frappe-bench

# Get ERPNext
RUN bench get-app --branch ${ERPNEXT_BRANCH} erpnext

# Copy setup and entrypoint scripts
COPY --chown=frappe:frappe entrypoint.sh /home/frappe/entrypoint.sh
COPY --chown=frappe:frappe setup_site.py /home/frappe/setup_site.py
RUN chmod +x /home/frappe/entrypoint.sh

EXPOSE 8000 9000

ENTRYPOINT ["/home/frappe/entrypoint.sh"]
