"""
Flask Bank Management CRUD Application
========================================
This application provides a RESTful API and web interface for managing bank records.
It demonstrates full CRUD operations with Microsoft SQL Server database.

Author: Nick Psyrras
Date: 2025
"""

from flask import Flask, render_template, redirect, url_for, flash
import pyodbc
from contextlib import contextmanager
import logging

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'af95e657e0c8bd551aba2b00a292dfb0c02a3211a7cb361bcfd332a9225f2091'


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DATABASE CONFIGURATION
DB_CONFIG = {
    'server': 'localhost',  # SQL Server instance address
    'database': 'BanksDB',   # Database name
    'username': 'your_username',  # SQL Server username
    'password': 'your_password',  # SQL Server password
    'driver': '{ODBC Driver 17 for SQL Server}'  # ODBC driver version
}


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
            f"PWD={DB_CONFIG['password']}"
        )
        
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
@app.route('/')
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
        return render_template('index.html', banks=banks)
        
    except Exception as e:
        logger.error(f"Error fetching banks: {e}")
        flash(f'Error fetching banks: {str(e)}', 'danger')
        return render_template('index.html', banks=[])



# APPLICATION ENTRY POINT
if __name__ == '__main__':

    try:
        # Initialize database and create tables if needed
        init_database()
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

@app.route('/bank/<int:bank_id>')
def view_bank(bank_id):
    """
    Display details for a specific bank.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Use parameterized query to prevent SQL injection
            cursor.execute("SELECT id, name, location FROM banks WHERE id = ?", (bank_id,))
            bank = cursor.fetchone()
        
        if bank:
            logger.info(f"Retrieved bank with ID: {bank_id}")
            return render_template('view_bank.html', bank=bank)
        else:
            logger.warning(f"Bank with ID {bank_id} not found")
            flash('Bank not found', 'warning')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Error fetching bank {bank_id}: {e}")
        flash(f'Error fetching bank: {str(e)}', 'danger')
        return redirect(url_for('index'))