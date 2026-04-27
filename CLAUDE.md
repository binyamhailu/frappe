# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-container ERPNext v15 deployment plus one custom Frappe app (`transport`) that models trip-based logistics: Trucks, Drivers, Routes, Transport Orders, and Trips with planned-vs-actual cost tracking and profitability. This is a POC — there is no standalone bench checkout; the bench is built inside the Docker image.

## Commands

All development happens through Docker Compose. There is no local Python/Node workflow.

```bash
docker compose up --build        # Build image + start stack (first run: ~10–15 min)
docker compose up                # Subsequent starts
docker compose down              # Stop
docker compose down -v           # Wipe MariaDB + sites volumes (fresh install)
```

Ports: app on `8000`, socketio on `9000`, MariaDB on `3307` (host) → `3306` (container). Default login: `Administrator` / `admin123` at http://localhost:8000.

Run bench commands inside the running container:

```bash
docker compose exec erpnext bash                                    # shell into container
docker compose exec erpnext bench --site erp.localhost migrate
docker compose exec erpnext bench --site erp.localhost console      # Python REPL with frappe loaded
docker compose exec erpnext bench --site erp.localhost execute transport.test_e2e.run
docker compose exec erpnext bench --site erp.localhost execute transport.setup_and_test.run
docker compose exec erpnext bench --site erp.localhost execute transport.setup_site.run  # demo data (re)load
docker compose exec erpnext bench build --app transport             # rebuild JS assets after JS changes
docker compose exec erpnext bench --site erp.localhost clear-cache
```

"Tests" in this repo are the `run()` scripts in `apps/transport/transport/test_e2e.py` and `setup_and_test.py` — they wipe the Trip/Order/Truck/Driver/Route data, create fixtures, exercise the trip lifecycle, and print a summary. There is no pytest/unittest harness configured.

Lint/format (from `apps/transport/README.md`): `pre-commit` runs ruff, eslint, prettier, pyupgrade. Install with `cd apps/transport && pre-commit install`. Ruff config lives in `apps/transport/pyproject.toml` (tabs, line length 110, `quote-style = "double"`).

## Architecture

### The container's moving parts

`Dockerfile` builds a full frappe-bench at `/home/frappe/frappe-bench` containing: `frappe` (version-15), `erpnext` (version-15), and `transport` (copied from `./apps/transport`). `transport` is `pip install -e`'d and appended to `sites/apps.txt`. Assets are `bench build`'d into the image.

`entrypoint.sh` runs on every container start and is the key piece to understand:

1. Writes Redis URLs into `common_site_config.json` via `bench set-config -g`.
2. **Re-syncs the transport app from the host mount** (`/home/frappe/custom-apps/transport` → `apps/transport`) with `rsync`, excluding `.git`/`node_modules`/`__pycache__`, then re-runs `pip install -e`. This means **Python edits to `apps/transport/` on the host propagate after a container restart** — no rebuild required. JS edits require `bench build --app transport`.
3. First run only: creates the MariaDB site `erp.localhost`, installs `erpnext` and `transport`, and runs `transport.setup_and_test.run` (or `setup_site.run`) to load demo data.
4. Subsequent runs: `bench migrate` then `bench start` (which launches gunicorn + workers + socketio via Procfile).

Site data lives in the `sites-data` named volume (`/home/frappe/frappe-bench/sites`). Wiping it via `down -v` triggers the first-run path again.

### Frappe app layout

Standard Frappe app structure under `apps/transport/transport/`. Wiring lives in `hooks.py`:

- `doctype_js` / `doctype_list_js`: attach custom client scripts to Trip and Transport Order.
- `override_doctype_dashboards`: each of Trip/Transport Order/Truck/Driver has a `*_dashboard.py` exposing connected docs (e.g. Sales Invoice on Trip).
- `required_apps = ["frappe", "erpnext"]` — Transport depends on ERPNext (Customer, Sales Invoice, Company).

DocTypes (`transport/transport/doctype/`): `truck`, `driver`, `route`, `transport_order`, `trip`, plus child tables `trip_planned_cost` and `trip_actual_cost`. Reports live in `transport/transport/report/` (six query reports registered in the Frappe workspace). A custom page `transport_dashboard` renders KPIs.

### Trip lifecycle (the core domain logic)

`trip.py` is where the interesting behavior sits. All calculations run in `validate()`:

- `calculate_actual_costs` pairs each actual-cost row against the planned-cost row with the same `cost_type` and writes `variance = actual - planned` onto the child row.
- `calculate_variance` derives `total_variance`, `variance_percentage`, and sets `budget_status` ∈ {Under Budget, On Budget, Over Budget, ""}.
- `calculate_profitability` sets `gross_profit = revenue - total_actual_cost` and `profit_margin`.

State transitions are whitelisted methods, not docstatus submissions: `start_trip` (Draft → In Progress, stamps `actual_start_date`), `complete_trip` (In Progress → Completed, stamps delivery date), `close_trip` (Completed → Closed, locks edits via `before_save`), `create_sales_invoice` (builds an ERPNext Sales Invoice and stores its name on the Trip). The Trip form's `trip.js` adds Actions-menu buttons that call these methods based on current status. Transport Order's status is not independently maintained — `TransportOrder.update_status_from_trips` rolls up child Trip statuses on validate.

### Gotcha from git history

The `apps.txt` in the bench must end with a newline, otherwise `transport` gets concatenated to `erpnext` on the previous line and the install fails silently. The `Dockerfile` uses `printf "\ntransport\n" >>` specifically for this reason (see commit `4a1f885`). Preserve that when editing.
