import os
import sqlite3
import logging
from src.models.interval import IntervalCondition, Interval
from src.models.well import Well
from src.models.photo import Photo


class DataBaseManager:
    def __init__(self, project):
        database_dir = os.path.join(project.path, "database")
        db_path = os.path.join(database_dir, f"{project.name}_geo_photo_database.db")
        os.makedirs(database_dir, exist_ok=True)
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self.setup_database()
        logging.info("DatabaseManager initialized for project: %s", project.name)

    def setup_database(self):
        # Create tables if not exist
        queries = [
            '''CREATE TABLE IF NOT EXISTS Wells(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
                )''',
            '''CREATE TABLE IF NOT EXISTS Intervals(
                id INTEGER PRIMARY KEY,
                version INTEGER NOT NULL DEFAULT 1,
                well_id INTEGER NOT NULL,
                interval_from REAL NOT NULL,
                interval_to REAL NOT NULL,
                condition TEXT NOT NULL,
                is_marked BOOLEAN NOT NULL,
                FOREIGN KEY(well_id) REFERENCES Wells(id) ON DELETE CASCADE
                )''',
            '''CREATE TABLE IF NOT EXISTS Photos(
                id INTEGER PRIMARY KEY,
                photo_path TEXT NOT NULL,
                interval_id INTEGER NOT NULL,
                FOREIGN KEY(interval_id) REFERENCES Intervals(id) ON DELETE CASCADE
                )'''
        ]
        for query in queries:
            self.cursor.execute(query)
        self.connection.commit()
        logging.info("Database tables set up successfully.")

    def get_well(self, well_id):
        """Retrieve a single well by its ID."""
        self.cursor.execute("SELECT * FROM Wells WHERE id = ?", (well_id,))
        well_data = self.cursor.fetchone()
        if well_data:
            return Well(well_data[0], well_data[1])
        logging.warning("No well found with ID: %s", well_id)
        return None

    def get_all_wells(self):
        """Retrieve all wells."""
        self.cursor.execute("SELECT * FROM Wells")
        wells_data = self.cursor.fetchall()
        return [Well(row[0], row[1]) for row in wells_data]

    def get_interval(self, interval_id):
        """Retrieve a single interval by its ID."""
        self.cursor.execute("SELECT * FROM Intervals WHERE id = ?", (interval_id,))
        row = self.cursor.fetchone()
        if row:
            return Interval(row[0], row[1], row[2], row[3], row[4], IntervalCondition[row[5].upper()], row[6])
        logging.warning("No interval found with ID: %s", interval_id)
        return None

    def get_all_intervals_by_well_id(self, well_id):
        """Retrieve all intervals associated with a specific well."""
        self.cursor.execute("SELECT * FROM Intervals WHERE well_id = ?", (well_id,))
        intervals_data = self.cursor.fetchall()
        return [Interval(row[0], row[1], well_id, row[3], row[4], IntervalCondition[row[5].upper()], row[6]) for row in
                intervals_data]

    def get_photo(self, photo_id):
        """Retrieve a single photo by its ID."""
        self.cursor.execute("SELECT * FROM Photos WHERE id = ?", (photo_id,))
        row = self.cursor.fetchone()
        if row:
            return Photo(row[0], row[1], row[2])
        logging.warning("No photo found with ID: %s", photo_id)
        return None

    def get_all_photos_by_interval_id(self, interval_id):
        """Retrieve all photos associated with a specific interval."""
        self.cursor.execute("SELECT * FROM Photos WHERE interval_id = ?", (interval_id,))
        photos_data = self.cursor.fetchall()
        return [Photo(row[0], row[1], row[2]) for row in photos_data]

    def add_well(self, name):
        """Adds a new well to the Wells table."""
        try:
            self.cursor.execute("INSERT INTO Wells (name) VALUES (?)", (name,))
            self.connection.commit()
            well_id = self.cursor.lastrowid
            logging.info("New well added with ID: %s", well_id)
            return well_id
        except sqlite3.Error as e:
            logging.error("Failed to add well '%s': %s", name, e)
            return None

    def get_max_version(self, settings, well_id):
        """Retrieves the maximum version number for a given interval and well."""
        query = """SELECT MAX(version) FROM Intervals WHERE well_id = ? AND interval_from = ? AND interval_to = ?"""
        self.cursor.execute(query, (well_id, settings.interval_from, settings.interval_to))
        return self.cursor.fetchone()[0]

    def add_interval(self, well_id, interval_settings):
        """Inserts a new interval into the database with automatic version management."""
        # Получаем текущую максимальную версию для данного интервала
        self.cursor.execute("""
            SELECT MAX(version) FROM Intervals 
            WHERE well_id = ? AND interval_from = ? AND interval_to = ? AND condition = ? AND is_marked = ?
        """, (well_id, interval_settings.interval_from, interval_settings.interval_to, interval_settings.condition.name,
              interval_settings.is_marked))

        max_version = self.cursor.fetchone()[0]
        new_version = (max_version or 0) + 1  # Если версия не найдена, начинаем с 1

        # Вставляем новый интервал с увеличенной версией
        query = """
            INSERT INTO Intervals (interval_from, interval_to, well_id, condition, is_marked, version)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (
            interval_settings.interval_from,
            interval_settings.interval_to,
            well_id,
            interval_settings.condition.name,
            interval_settings.is_marked,
            new_version
        ))
        self.connection.commit()

        logging.info(f"Added new interval with version {new_version} for well ID {well_id}.")
        return self.cursor.lastrowid

    def add_photo(self, path, interval_id):
        """Adds a photo record linked to an interval."""
        query = "INSERT INTO Photos (photo_path, interval_id) VALUES (?, ?)"
        self.cursor.execute(query, (path, interval_id))

    def close_connection(self):
        """Close the database connection."""
        self.connection.close()
        logging.info("Database connection closed.")

