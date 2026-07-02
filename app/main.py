import os
import time

import mysql.connector
from fastapi import FastAPI, HTTPException


app = FastAPI(
    title="FastAPI DevOps Task 6",
    description="A FastAPI app containerized with Docker Compose and connected to MySQL.",
    version="1.0.0",
)


def get_db_connection(max_attempts: int = 5, delay_seconds: int = 2):
    """Create a MySQL connection with retry logic."""
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            return mysql.connector.connect(
                host=os.getenv("DB_HOST", "db"),
                port=int(os.getenv("DB_PORT", "3306")),
                database=os.getenv("DB_NAME", os.getenv("MYSQL_DATABASE", "employees")),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                connection_timeout=5,
            )
        except mysql.connector.Error as error:
            last_error = error
            if attempt < max_attempts:
                time.sleep(delay_seconds)

    raise last_error


@app.get("/")
def read_root() -> dict[str, str]:
    """Return a small welcome message and status response."""
    return {
        "message": "Welcome to the FastAPI DevOps Task 6 API.",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "db_health": "/db/health",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a basic health check response."""
    return {
        "status": "OK",
        "service": "fastapi-task6",
    }


@app.get("/db/health")
def db_health_check() -> dict[str, str]:
    """Check whether the app can connect to MySQL."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        return {
            "status": "OK",
            "service": "fastapi-task6",
            "database": "connected",
            "db_host": os.getenv("DB_HOST", "db"),
            "result": str(result[0]),
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {error}",
        )


@app.get("/employees/count")
def employee_count() -> dict[str, int | str]:
    """Return the number of employees in the Employees sample database."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees;")
        count = cursor.fetchone()[0]
        cursor.close()
        connection.close()

        return {
            "database": os.getenv("DB_NAME", "employees"),
            "table": "employees",
            "employee_count": count,
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Could not query employees table: {error}",
        )