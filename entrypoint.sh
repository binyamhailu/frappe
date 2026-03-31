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

# Wait for MariaDB
echo "Waiting for MariaDB..."
while ! mariadb-admin ping -h"${DB_HOST}" -P"${DB_PORT}" -p"${DB_ROOT_PASSWORD}" --silent 2>/dev/null; do
    sleep 2
done
echo "MariaDB is ready!"

# Create site if it doesn't exist
if [ ! -d "sites/${SITE_NAME}" ]; then
    echo "Creating new site: ${SITE_NAME}"
    bench new-site "${SITE_NAME}" \
        --db-host "${DB_HOST}" \
        --db-port "${DB_PORT}" \
        --db-root-password "${DB_ROOT_PASSWORD}" \
        --admin-password "${ADMIN_PASSWORD}" \
        --install-app erpnext

    bench use "${SITE_NAME}"

    # Install transport app if available
    if [ -d "/home/frappe/custom-apps/transport" ]; then
        echo "Installing Transport module..."
        cp -r /home/frappe/custom-apps/transport "$BENCH_DIR/apps/transport"
        cd "$BENCH_DIR/apps/transport"
        pip install -e . --quiet 2>/dev/null || true
        cd "$BENCH_DIR"
        bench --site "${SITE_NAME}" install-app transport
    fi

    # Run setup script to create demo data
    if [ -f "/home/frappe/setup_site.py" ]; then
        echo "Loading demo data..."
        bench --site "${SITE_NAME}" execute transport.setup_and_test.run 2>/dev/null || \
        bench --site "${SITE_NAME}" execute setup_site.run 2>/dev/null || \
        echo "Demo data setup skipped (run manually later)"
    fi

    echo ""
    echo "============================================"
    echo "  ERP Site created successfully!"
    echo "  URL:      http://localhost:8000"
    echo "  User:     Administrator"
    echo "  Password: ${ADMIN_PASSWORD}"
    echo "============================================"
    echo ""
else
    echo "Site ${SITE_NAME} already exists"
    bench use "${SITE_NAME}"

    # Re-copy transport app if updated
    if [ -d "/home/frappe/custom-apps/transport" ]; then
        echo "Updating Transport module..."
        rsync -a --delete /home/frappe/custom-apps/transport/ "$BENCH_DIR/apps/transport/" 2>/dev/null || \
        cp -r /home/frappe/custom-apps/transport "$BENCH_DIR/apps/transport"
        cd "$BENCH_DIR/apps/transport"
        pip install -e . --quiet 2>/dev/null || true
        cd "$BENCH_DIR"
        bench --site "${SITE_NAME}" migrate 2>/dev/null || true
    fi
fi

# Build assets
bench build --app transport 2>/dev/null || true

echo "Starting ERPNext..."
bench start
