#!/bin/bash
set -e

BENCH_DIR="/home/frappe/frappe-bench"
SITE_NAME="${SITE_NAME:-erp.localhost}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"

cd "$BENCH_DIR"

# Configure Redis connections
bench set-config -g redis_cache "${REDIS_CACHE}"
bench set-config -g redis_queue "${REDIS_QUEUE}"
bench set-config -g redis_socketio "${REDIS_CACHE}"

# If transport app source is mounted (for live updates), sync it
if [ -d "/home/frappe/custom-apps/transport" ]; then
    echo "Syncing Transport app from mount..."
    rsync -a --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
        /home/frappe/custom-apps/transport/ "$BENCH_DIR/apps/transport/"
    cd "$BENCH_DIR"
    ./env/bin/pip install -e ./apps/transport --quiet 2>/dev/null || true
fi

# Wait for MariaDB
echo "Waiting for MariaDB..."
while ! mariadb-admin ping -h"${DB_HOST}" -P"${DB_PORT}" -p"${DB_ROOT_PASSWORD}" --silent 2>/dev/null; do
    sleep 2
done
echo "MariaDB is ready!"

# Create site if it doesn't exist
if [ ! -d "sites/${SITE_NAME}" ]; then
    echo ""
    echo "=========================================="
    echo "  First run - setting up ERPNext site..."
    echo "  This takes a few minutes."
    echo "=========================================="
    echo ""

    bench new-site "${SITE_NAME}" \
        --db-host "${DB_HOST}" \
        --db-port "${DB_PORT}" \
        --db-root-password "${DB_ROOT_PASSWORD}" \
        --admin-password "${ADMIN_PASSWORD}" \
        --install-app erpnext

    bench use "${SITE_NAME}"

    # Install transport app on the site (creates DB tables)
    echo "Installing Transport module..."
    bench --site "${SITE_NAME}" install-app transport

    echo ""
    echo "============================================"
    echo ""
    echo "  ERP is ready! (clean install)"
    echo ""
    echo "  URL:      http://localhost:8000"
    echo "  User:     Administrator"
    echo "  Password: ${ADMIN_PASSWORD}"
    echo ""
    echo "  Transport: http://localhost:8000/app/transport"
    echo ""
    echo "  To load demo data, run:"
    echo "  docker exec -it erp-app bench --site erp.localhost execute transport.demo.load"
    echo ""
    echo "============================================"
    echo ""
else
    echo "Site ${SITE_NAME} exists - running migrations..."
    bench use "${SITE_NAME}"
    bench --site "${SITE_NAME}" migrate 2>/dev/null || true
fi

echo "Starting ERPNext..."
bench start
