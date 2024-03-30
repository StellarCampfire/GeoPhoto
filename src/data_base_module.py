import os
import sqlite3
import logging
from src.models import IntervalCondition, Project, Well, Interval, Photo


class DBManager:
    def __init__(self, project):
        database_dir = os.path.join(project.path, "database")
        db_path = os.path.join(database_dir, f"{project.name}_geo_photo_database.db")

        os.makedirs(database_dir, exist_ok=True)

        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self.setup_database()

    def setup_database(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Wells(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Intervals(
            id INTEGER PRIMARY KEY,
            version INTEGER NOT NULL DEFAULT 1,
            well_id INTEGER NOT NULL,    
            interval_from REAL NOT NULL,
            interval_to REAL NOT NULL,
            condition TEXT NOT NULL,  
            is_marked BOOLEAN NOT NULL,        
            FOREIGN KEY(well_id) REFERENCES Wells(id) ON DELETE CASCADE
            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Photos(
            id INTEGER PRIMARY KEY,
            photo_path TEXT NOT NULL,
            interval_id INTEGER NOT NULL,
            order_num INTEGER,
            FOREIGN KEY(interval_id) REFERENCES Intervals(id) ON DELETE CASCADE
            )''')
        self.connection.commit()

    def add_project(self, name):
        try:
            self.cursor.execute("INSERT INTO Projects (name) VALUES (?)", (name,))
            self.connection.commit()
            project_id = self.cursor.lastrowid
            return self.get_project(project_id)
        except sqlite3.Error as e:
            logging.error(f'Error adding project "{name}": {e}')
        return None

    def delete_project(self, project_id):
        self.cursor.execute("DELETE FROM Projects WHERE id = ?", (str(project_id),))
        self.connection.commit()

    def update_project(self, project_id, new_name):
        self.cursor.execute("UPDATE Projects SET name = ? WHERE id = ?", (new_name, str(project_id)))
        self.connection.commit()

    def get_project(self, project_id):
        self.cursor.execute("SELECT * FROM Projects WHERE id = ?", (str(project_id),))
        project_data = self.cursor.fetchone()
        if project_data:
            project = {
                'id': project_data[0],
                'name': project_data[1]
            }
            return project
        else:
            return None

    def get_all_projects(self):
        self.cursor.execute("SELECT * FROM Projects")
        projects_data = self.cursor.fetchall()
        projects = []
        for project_row in projects_data:
            project = {
                'id': project_row[0],
                'name': project_row[1]
            }
            projects.append(project)
        return projects

    # def add_well(self, name, project_id):
    #     try:
    #         self.cursor.execute("INSERT INTO Wells (name, project_id) VALUES (?, ?)", (name, str(project_id)))
    #         self.connection.commit()
    #         well_id = self.cursor.lastrowid
    #         return self.get_well(well_id)
    #     except sqlite3.Error as e:
    #         logging.error(f'Error adding well "{name}": {e}')
    #         return None

    # def add_well(self, name, project_id):
    #     try:
    #         self.cursor.execute("INSERT INTO Wells (name) VALUES (?)", (name))
    #         self.connection.commit()
    #         well_id = self.cursor.lastrowid
    #         return self.get_well(well_id)
    #     except sqlite3.Error as e:
    #         logging.error(f'Error adding well "{name}": {e}')
    #         return None

    def add_well(self, name):
        try:
            self.cursor.execute("INSERT INTO Wells (name) VALUES (?)", (name,))
            self.connection.commit()
            well_id = self.cursor.lastrowid
            logging.info(f'New well with ID: {well_id} created.')
            return well_id
        except sqlite3.Error as e:
            logging.error(f'Error adding well "{name}": {e}')
            return None


    def delete_well(self, well_id):
        self.cursor.execute("DELETE FROM Wells WHERE id = ?", str(well_id))
        self.connection.commit()

    def update_well(self, well_id, new_name):
        self.cursor.execute("UPDATE Wells SET name = ? WHERE id = ?", (new_name, str(well_id)))
        self.connection.commit()

    def get_well(self, well_id):
        self.cursor.execute("SELECT * FROM Wells WHERE id = ?", (str(well_id),))
        well_data = self.cursor.fetchone()
        if well_data:
            well = Well(
                well_data[0],
                well_data[1])
            return well
        else:
            return None

    def get_all_wells(self):
        self.cursor.execute("SELECT * FROM Wells")
        wells_data = self.cursor.fetchall()
        wells = []
        for well_row in wells_data:
            well = Well(
                well_row[0],
                well_row[1])
            wells.append(well)
        return wells

    def add_interval(self, interval_from, interval_to, well_id):
        self.cursor.execute("INSERT INTO Intervals (interval_from, interval_to, well_id) VALUES (?, ?, ?)",
                            (str(interval_from), str(interval_to), str(well_id)))
        self.connection.commit()
        interval_id = self.cursor.lastrowid
        return self.get_interval(interval_id)

    def delete_interval(self, interval_id):
        self.cursor.execute("DELETE FROM Intervals WHERE id = ?", (str(interval_id),))
        self.connection.commit()

    def update_interval(self, interval_id, new_from, new_to):
        self.cursor.execute("UPDATE Intervals SET interval_from = ?, interval_to = ? WHERE id = ?",
                            (new_from, new_to, str(interval_id)))
        self.connection.commit()

    def get_interval(self, interval_id):
        self.cursor.execute("SELECT * FROM Intervals WHERE id = ?", (str(interval_id),))
        interval_data = self.cursor.fetchone()
        if interval_data:
            condition = IntervalCondition[interval_data[5].upper()]
            interval = Interval(
                interval_data[0],
                interval_data[1],
                interval_data[2],
                interval_data[3],
                interval_data[4],
                condition,
                interval_data[6],
            )
            return interval
        else:
            return None

    def get_all_intervals_by_well_id(self, well_id):
        self.cursor.execute("SELECT * FROM Intervals WHERE well_id = ?", str(well_id))
        intervals_data = self.cursor.fetchall()
        intervals = []
        for interval_row in intervals_data:
            condition = IntervalCondition[interval_row[5].upper()]
            interval = Interval(
                interval_row[0],
                interval_row[1],
                interval_row[2],
                interval_row[3],
                interval_row[4],
                condition,
                interval_row[6],
            )
            intervals.append(interval)
        return intervals

    def add_photo(self, photo_path, interval_id, order_num):
        self.cursor.execute("INSERT INTO Photos (photo_path, interval_id, order_num) VALUES (?, ?, ?)",
                            (photo_path, str(interval_id), str(order_num)))
        self.connection.commit()

    def delete_photo(self, photo_id):
        self.cursor.execute("DELETE FROM Photos WHERE id = ?", (str(photo_id),))
        self.connection.commit()

    def update_photo(self, photo_id, new_path, new_order):
        self.cursor.execute("UPDATE Photos SET photo_path = ?, order_num = ? WHERE id = ?",
                            (new_path, str(new_order), str(photo_id)))
        self.connection.commit()

    def get_photo(self, photo_id):
        self.cursor.execute("SELECT * FROM Photos WHERE id = ?", (str(photo_id),))
        photo_data = self.cursor.fetchone()
        if photo_data:
            photo = Photo(
                photo_data[0],
                photo_data[1],
                photo_data[2],
            )
            return photo
        else:
            return None

    def get_all_photos_by_interval_id(self, interval_id):
        self.cursor.execute("SELECT * FROM Photos WHERE interval_id = ?", (interval_id,))
        photos_data = self.cursor.fetchall()
        photos = []
        for photo_row in photos_data:
            photo = Photo(
                photo_row[0],
                photo_row[1],
                photo_row[2],
            )
            photos.append(photo)
        return photos

    def create_interval_with_photos(self, well_id, interval_settings, photo_paths):
        try:
            self.connection.execute("BEGIN")  # Начало транзакции

            self.cursor.execute("""
                            SELECT MAX(version) FROM Intervals
                            WHERE interval_from = ? AND interval_to = ? AND well_id = ? AND condition = ? AND is_marked = ?""",
                                (interval_settings.interval_from,
                                 interval_settings.interval_to,
                                 well_id,
                                 interval_settings.condition.name,
                                 interval_settings.is_marked))

            result = self.cursor.fetchone()
            max_version = result[0] if result[0] is not None else 0

            new_version = max_version + 1
            self.cursor.execute("""
                            INSERT INTO Intervals (interval_from, interval_to, well_id, condition, is_marked, version)
                            VALUES (?, ?, ?, ?, ?, ?)""",
                                (interval_settings.interval_from,
                                 interval_settings.interval_to, well_id,
                                 interval_settings.condition.name,
                                 interval_settings.is_marked,
                                 new_version))

            interval_id = self.cursor.lastrowid  # Получаем ID только что созданного интервала

            for order_num, photo_path in enumerate(photo_paths, start=1):
                self.cursor.execute("INSERT INTO Photos (photo_path, interval_id, order_num) VALUES (?, ?, ?)",
                                    (photo_path, interval_id, order_num))

            self.connection.commit()  # Подтверждаем транзакцию, если все запросы выполнены успешно

            return True, interval_id  # Возвращаем ID созданного интервала после успешной транзакции
        except sqlite3.Error as e:
            logging.error(
                f"Ошибка при создании интервала {str(interval_settings['interval_from'])} - "
                f"{str(interval_settings['interval_to'])}, разметка: {str(interval_settings.is_marked)}, "
                f"состояние: {interval_settings.condition.name}, с фотографиями: {e}")
            self.connection.rollback()  # Откатываем транзакцию в случае ошибки
            return False, None

    def close_connection(self):
        self.connection.close()
