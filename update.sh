#!/bin/bash

# update.sh
# Usage: ./update.sh
# Pulls the latest code from GitHub, rebuilds and recreates Docker Compose containers,
# verifies the FastAPI and database health endpoints, and logs the result.

set -u

BRANCH="main"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/update.log"

log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

endlog() {
    echo "--------------------------END OF UPDATE--------------------------" >> "$LOG_FILE"
}

fail() {
    log "UPDATE FAILED: $1"
    endlog
    exit 1
}

checkstatus() {
    if [ "$1" -ne 0 ]; then
        fail "$2"
    fi
}

mkdir -p "$LOG_DIR" || exit 1

log "Update started."
log "Project directory: $PROJECT_DIR"

cd "$PROJECT_DIR" || fail "Could not enter project directory."

log "Pulling latest changes from GitHub."

git pull --ff-only origin "$BRANCH" >> "$LOG_FILE" 2>&1
checkstatus $? "Git pull failed."

log "Git pull completed successfully."

log "Rebuilding and recreating Docker Compose containers."

docker compose up -d --build >> "$LOG_FILE" 2>&1
checkstatus $? "Docker Compose deployment failed."

log "Docker Compose deployment completed."

log "Current Docker Compose status:"
docker compose ps >> "$LOG_FILE" 2>&1
checkstatus $? "Could not get Docker Compose status."

log "Waiting briefly before health checks."
sleep 5

log "Checking FastAPI health endpoint."

curl -fsS http://127.0.0.1:8000/health >> "$LOG_FILE" 2>&1
checkstatus $? "FastAPI health check failed."

log "FastAPI health check passed."

log "Checking database health endpoint."

curl -fsS http://127.0.0.1:8000/db/health >> "$LOG_FILE" 2>&1
checkstatus $? "Database health check failed."

log "Database health check passed."

log "Update completed successfully."
endlog