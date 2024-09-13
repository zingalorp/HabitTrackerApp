import sqlite3
import datetime
from habit import Habit

# Define the SQLiteDB class to handle database interaction
class SQLiteDB:
    def __init__(self, db_name='habits.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS Habits (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        description TEXT,
                        periodicity TEXT,
                        creationDate TEXT,
                        streak INTEGER,
                        lastCompletionDate TEXT,
                        category TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS CompletionRecords (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        habit_id INTEGER,
                        completionDate TEXT,
                        FOREIGN KEY (habit_id) REFERENCES Habits(id)
                    )''')
        self.conn.commit()

    def storeHabit(self, habit):
        c = self.conn.cursor()
        c.execute('''INSERT INTO Habits (title, description, periodicity, creationDate, streak, lastCompletionDate, category)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (habit.title, habit.description, habit.periodicity, habit.creationDate.isoformat(),
                   habit.streak, habit.lastCompletionDate.isoformat() if habit.lastCompletionDate else None,
                   habit.category))
        self.conn.commit()
        return c.lastrowid

    def updateHabit(self, habit_id, habit):
        c = self.conn.cursor()
        c.execute('''UPDATE Habits SET title=?, description=?, periodicity=?, category=?, streak=?, lastCompletionDate=? WHERE id=?''',
                  (habit.title, habit.description, habit.periodicity, habit.category, habit.streak,
                   habit.lastCompletionDate.isoformat() if habit.lastCompletionDate else None, habit_id))
        self.conn.commit()

    def deleteHabit(self, habit_id):
        c = self.conn.cursor()
        c.execute('''DELETE FROM Habits WHERE id=?''', (habit_id,))
        c.execute('''DELETE FROM CompletionRecords WHERE habit_id=?''', (habit_id,))
        self.conn.commit()

    def clearTables(self):
        c = self.conn.cursor()
        c.execute('''DELETE FROM Habits''')
        c.execute('''DELETE FROM CompletionRecords''')
        # Reset the autoincrement by deleting the relevant row in sqlite_sequence
        c.execute('''DELETE FROM sqlite_sequence WHERE name='Habits' ''')
        c.execute('''DELETE FROM sqlite_sequence WHERE name='CompletionRecords' ''')
        self.conn.commit()

    def storeCompletionRecord(self, habit_id, date):
        c = self.conn.cursor()
        c.execute('''INSERT INTO CompletionRecords (habit_id, completionDate)
                     VALUES (?, ?)''', (habit_id, date.isoformat()))
        self.conn.commit()

    def getHabit(self, habit_id):
        c = self.conn.cursor()
        c.execute('''SELECT * FROM Habits WHERE id=?''', (habit_id,))
        row = c.fetchone()
        if row:
            habit = Habit(row[1], row[2], row[3], row[7])
            habit.creationDate = datetime.date.fromisoformat(row[4])
            habit.streak = row[5]
            habit.lastCompletionDate = datetime.date.fromisoformat(row[6]) if row[6] else None
            habit.completionHistory = self.getCompletionHistory(habit_id)
            return habit
        else:
            return None

    def getAllHabits(self):
        c = self.conn.cursor()
        c.execute('''SELECT * FROM Habits''')
        rows = c.fetchall()
        habits = []
        for row in rows:
            habit = Habit(row[1], row[2], row[3], row[7])
            habit.creationDate = datetime.date.fromisoformat(row[4])
            habit.streak = row[5]
            habit.lastCompletionDate = datetime.date.fromisoformat(row[6]) if row[6] else None
            habit_id = row[0]
            habit.completionHistory = self.getCompletionHistory(habit_id)
            habits.append((habit_id, habit))
        return habits

    def getCompletionHistory(self, habit_id):
        c = self.conn.cursor()
        c.execute('''SELECT completionDate FROM CompletionRecords WHERE habit_id=?''', (habit_id,))
        dates = c.fetchall()
        return [datetime.date.fromisoformat(d[0]) for d in dates]

    def getHabitsByPeriodicity(self, periodicity):
        c = self.conn.cursor()
        c.execute('''SELECT * FROM Habits WHERE periodicity=?''', (periodicity,))
        rows = c.fetchall()
        habits = []
        for row in rows:
            habit = Habit(row[1], row[2], row[3], row[7])
            habit.creationDate = datetime.date.fromisoformat(row[4])
            habit.streak = row[5]
            habit.lastCompletionDate = datetime.date.fromisoformat(row[6]) if row[6] else None
            habit_id = row[0]
            habit.completionHistory = self.getCompletionHistory(habit_id)
            habits.append((habit_id, habit))
        return habits

    def close(self):
        self.conn.close()