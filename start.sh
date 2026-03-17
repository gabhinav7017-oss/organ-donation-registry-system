#!/bin/bash
set -e

# Ensure we're in the project directory
cd /opt/render/project/src || cd "$(dirname "$0")"

# Export Python path to ensure Django can be found
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run gunicorn from the project root
exec gunicorn organ_donation.wsgi:application --bind 0.0.0.0:${PORT:-8000}
