"""
Flask Bank Management CRUD Application
========================================
This application provides a RESTful API and web interface for managing bank records.
It demonstrates full CRUD operations with Microsoft SQL Server database.

Author: Nick Psyrras
Date: 2025
"""

from flask import Flask, jsonify, render_template, redirect, request, url_for, flash
import pyodbc
from dotenv import load_dotenv
import os
from contextlib import contextmanager
import logging

# Initialize Flask application
app = Flask(__name__)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app.secret_key = os.getenv("SECRET_KEY")

# DATABASE CONFIGURATION
DB_CONFIG = {
    "server": os.getenv("DB_SERVER"),
    "database": os.getenv("DB_NAME"),
    "username": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "driver": "{ODBC Driver 18 for SQL Server}",
}
print(DB_CONFIG)


# DATABASE CONNECTION MANAGEMENT
@contextmanager
def get_db_connection():
    conn = None
    try:
        # Create connection string
        connection_string = (
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']};"
            f"TrustServerCertificate=yes"
            # f"Encrypt=yes;"  # Enable encryption
        )
        print(connection_string)

        # Establish connection to SQL Server
        conn = pyodbc.connect(connection_string)
        logger.info("Database connection established")
        yield conn

    except pyodbc.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

    finally:
        # Always close connection to prevent resource leaks
        if conn:
            conn.close()
            logger.info("Database connection closed")


def init_database():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Create table only if it doesn't exist
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='banks' AND xtype='U')
                CREATE TABLE banks (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    name NVARCHAR(255) NOT NULL,
                    location NVARCHAR(255) NOT NULL
                )
            """)
            conn.commit()
            logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


# WEB INTERFACE ROUTES
@app.route("/")
def index():
    """
    Display list of all banks in the database.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Fetch all banks ordered by name
            cursor.execute("SELECT id, name, location FROM banks ORDER BY name")
            banks = cursor.fetchall()

        logger.info(f"Retrieved {len(banks)} banks from database")
        return render_template("index.html", banks=banks)

    except Exception as e:
        logger.error(f"Error fetching banks: {e}")
        flash(f"Error fetching banks: {str(e)}", "danger")
        return render_template("index.html", banks=[])


@app.route("/bank/<int:bank_id>")
def view_bank(bank_id):
    """
    Display details for a specific bank.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Use parameterized query to prevent SQL injection
            cursor.execute(
                "SELECT id, name, location FROM banks WHERE id = ?", (bank_id,)
            )
            bank = cursor.fetchone()

        if bank:
            logger.info(f"Retrieved bank with ID: {bank_id}")
            return render_template("view_bank.html", bank=bank)
        else:
            logger.warning(f"Bank with ID {bank_id} not found")
            flash("Bank not found", "warning")
            return redirect(url_for("index"))

    except Exception as e:
        logger.error(f"Error fetching bank {bank_id}: {e}")
        flash(f"Error fetching bank: {str(e)}", "danger")
        return redirect(url_for("index"))


@app.route("/bank/new", methods=["GET", "POST"])
def create_bank():
    """
    Create a new bank record.
    GET: Display form to create new bank
    POST: Process form submission and insert new bank into database
    """
    if request.method == "POST":
        # Extract form data
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()

        # Validate input
        if not name or not location:
            logger.warning("Validation failed: Name and location are required")
            flash("Name and location are required", "warning")
            return render_template("create_bank.html")

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Insert new bank using parameterized query
                cursor.execute(
                    "INSERT INTO banks (name, location) VALUES (?, ?)", (name, location)
                )
                conn.commit()

            logger.info(f"Bank created: {name} in {location}")
            flash("Bank created successfully!", "success")
            return redirect(url_for("index"))

        except Exception as e:
            logger.error(f"Error creating bank: {e}")
            flash(f"Error creating bank: {str(e)}", "danger")
            return render_template("create_bank.html")

    # GET request: Display form
    return render_template("create_bank.html")


@app.route("/bank/<int:bank_id>/edit", methods=["GET", "POST"])
def edit_bank(bank_id):
    """
    Update an existing bank record.
    GET: Display form pre-filled with current bank data
    POST: Process form submission and update bank in database
    """
    if request.method == "POST":
        # Extract and validate form data
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()

        if not name or not location:
            logger.warning(f"Validation failed for bank {bank_id}")
            flash("Name and location are required", "warning")
            return redirect(url_for("edit_bank", bank_id=bank_id))

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Update bank using parameterized query
                cursor.execute(
                    "UPDATE banks SET name = ?, location = ? WHERE id = ?",
                    (name, location, bank_id),
                )
                conn.commit()

            logger.info(f"Bank {bank_id} updated successfully")
            flash("Bank updated successfully!", "success")
            return redirect(url_for("view_bank", bank_id=bank_id))

        except Exception as e:
            logger.error(f"Error updating bank {bank_id}: {e}")
            flash(f"Error updating bank: {str(e)}", "danger")

    # GET request or error: Fetch and display current bank data
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, location FROM banks WHERE id = ?", (bank_id,)
            )
            bank = cursor.fetchone()

        if bank:
            return render_template("edit_bank.html", bank=bank)
        else:
            logger.warning(f"Bank {bank_id} not found for editing")
            flash("Bank not found", "warning")
            return redirect(url_for("index"))

    except Exception as e:
        logger.error(f"Error fetching bank {bank_id} for editing: {e}")
        flash(f"Error fetching bank: {str(e)}", "danger")
        return redirect(url_for("index"))


@app.route("/bank/<int:bank_id>/delete", methods=["POST"])
def delete_bank(bank_id):
    """
    Delete a bank record from the database.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Delete bank using parameterized query
            cursor.execute("DELETE FROM banks WHERE id = ?", (bank_id,))
            conn.commit()

        logger.info(f"Bank {bank_id} deleted successfully")
        flash("Bank deleted successfully!", "success")

    except Exception as e:
        logger.error(f"Error deleting bank {bank_id}: {e}")
        flash(f"Error deleting bank: {str(e)}", "danger")

    return redirect(url_for("index"))


# RESTful API endpoints
@app.route("/api/banks", methods=["GET"])
def api_get_banks():
    """
    RESTful API: Get all banks.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, location FROM banks ORDER BY name")
            banks = cursor.fetchall()

        # Convert database rows to dictionary format
        banks_list = [
            {"id": bank.id, "name": bank.name, "location": bank.location}
            for bank in banks
        ]

        logger.info(f"API: Retrieved {len(banks_list)} banks")
        return jsonify(
            {"success": True, "data": banks_list, "count": len(banks_list)}
        ), 200

    except Exception as e:
        logger.error(f"API error fetching banks: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/banks/<int:bank_id>", methods=["GET"])
def api_get_bank(bank_id):
    """
    RESTful API: Get a specific bank by ID.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, location FROM banks WHERE id = ?", (bank_id,)
            )
            bank = cursor.fetchone()

        if bank:
            logger.info(f"API: Retrieved bank {bank_id}")
            return jsonify(
                {
                    "success": True,
                    "data": {
                        "id": bank.id,
                        "name": bank.name,
                        "location": bank.location,
                    },
                }
            ), 200
        else:
            logger.warning(f"API: Bank {bank_id} not found")
            return jsonify({"success": False, "error": "Bank not found"}), 404

    except Exception as e:
        logger.error(f"API error fetching bank {bank_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/banks", methods=["POST"])
def api_create_bank():
    """
    RESTful API: Create a new bank.
    """
    try:
        # Parse JSON request body
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        # Extract and validate fields
        name = data.get("name", "").strip()
        location = data.get("location", "").strip()

        if not name or not location:
            logger.warning("API: Validation failed - name and location required")
            return jsonify(
                {"success": False, "error": "Name and location are required"}
            ), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Insert new bank
            cursor.execute(
                "INSERT INTO banks (name, location) VALUES (?, ?)", (name, location)
            )
            conn.commit()

            # Get the ID of the newly created bank
            cursor.execute("SELECT @@IDENTITY AS id")
            new_id = cursor.fetchone()[0]

        logger.info(f"API: Bank created with ID {new_id}")
        return jsonify(
            {
                "success": True,
                "data": {"id": new_id, "name": name, "location": location},
                "message": "Bank created successfully",
            }
        ), 201

    except Exception as e:
        logger.error(f"API error creating bank: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/banks/<int:bank_id>", methods=["PUT"])
def api_update_bank(bank_id):
    """
    RESTful API: Update an existing bank.
    """
    try:
        # Parse JSON request body
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        # Extract and validate fields
        name = data.get("name", "").strip()
        location = data.get("location", "").strip()

        if not name or not location:
            logger.warning(f"API: Validation failed for bank {bank_id}")
            return jsonify(
                {"success": False, "error": "Name and location are required"}
            ), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if bank exists
            cursor.execute("SELECT id FROM banks WHERE id = ?", (bank_id,))
            if not cursor.fetchone():
                logger.warning(f"API: Bank {bank_id} not found for update")
                return jsonify({"success": False, "error": "Bank not found"}), 404

            # Update bank
            cursor.execute(
                "UPDATE banks SET name = ?, location = ? WHERE id = ?",
                (name, location, bank_id),
            )
            conn.commit()

        logger.info(f"API: Bank {bank_id} updated successfully")
        return jsonify(
            {
                "success": True,
                "data": {"id": bank_id, "name": name, "location": location},
                "message": "Bank updated successfully",
            }
        ), 200

    except Exception as e:
        logger.error(f"API error updating bank {bank_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/banks/<int:bank_id>", methods=["DELETE"])
def api_delete_bank(bank_id):
    """
    RESTful API: Delete a bank.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if bank exists before deleting
            cursor.execute("SELECT id FROM banks WHERE id = ?", (bank_id,))
            if not cursor.fetchone():
                logger.warning(f"API: Bank {bank_id} not found for deletion")
                return jsonify({"success": False, "error": "Bank not found"}), 404

            # Delete bank
            cursor.execute("DELETE FROM banks WHERE id = ?", (bank_id,))
            conn.commit()

        logger.info(f"API: Bank {bank_id} deleted successfully")
        return jsonify({"success": True, "message": "Bank deleted successfully"}), 200

    except Exception as e:
        logger.error(f"API error deleting bank {bank_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# APPLICATION ENTRY POINT
if __name__ == "__main__":
    try:
        # Initialize database and create tables if needed
        init_database()

        app.run(debug=True, host="0.0.0.0", port=5001)

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
