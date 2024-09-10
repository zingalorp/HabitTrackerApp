import datetime

class Habit:
    def __init__(self, title, description=None, periodicity='daily', category=None):
        self.title = title
        self.description = description
        self.periodicity = periodicity  # 'daily' or 'weekly'
        self.creationDate = datetime.date.today()
        self.completionHistory = []
        self.streak = 0
        self.lastCompletionDate = None
        self.category = category

    def completeTask(self):
        today = datetime.date.today()
        self.completionHistory.append(today)
        self.updateStreak(today)
        self.lastCompletionDate = today

    def updateStreak(self, date):
        if self.lastCompletionDate is None:
            self.streak = 1
        else:
            delta = (date - self.lastCompletionDate).days
            if self.periodicity == 'daily' and delta == 1:
                self.streak += 1
            elif self.periodicity == 'weekly' and 7 <= delta < 14:
                self.streak += 1
            else:
                self.streak = 1

    def calculateStreak(self):
        # Recalculate streak based on completionHistory
        sorted_history = sorted(self.completionHistory)
        streak = 0
        last_date = None
        for date in sorted_history:
            if last_date is None:
                streak = 1
            else:
                delta = (date - last_date).days
                if self.periodicity == 'daily' and delta == 1:
                    streak += 1
                elif self.periodicity == 'weekly' and 7 <= delta < 14:
                    streak += 1
                else:
                    streak = 1
            last_date = date
        self.streak = streak
        return streak


import sqlite3

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
                     VALUES (?, ?)''',
                  (habit_id, date.isoformat()))
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

    def getLongestStreak(self):
        c = self.conn.cursor()
        c.execute('''SELECT MAX(streak) FROM Habits''')
        result = c.fetchone()
        return result[0] if result else 0

    def close(self):
        self.conn.close()


class Analytics:
    def __init__(self, db):
        self.db = db

    def calculateLongestStreakAll(self):
        habits = self.db.getAllHabits()
        max_streak = 0
        max_habit = None
        for habit_id, habit in habits:
            if habit.streak > max_streak:
                max_streak = habit.streak
                max_habit = habit
        if max_habit:
            print(f"Longest streak is {max_streak} for habit '{max_habit.title}'")
        else:
            print("No habits found.")

    def calculateLongestStreakForHabit(self, habit_id):
        habit = self.db.getHabit(habit_id)
        if habit:
            streak = habit.calculateStreak()
            print(f"Longest streak for habit '{habit.title}' is {streak}")
        else:
            print("Habit not found.")

    def analyseByCategory(self):
        habits = self.db.getAllHabits()
        categories = {}
        for habit_id, habit in habits:
            category = habit.category if habit.category else "Uncategorized"
            categories.setdefault(category, []).append(habit)
        for category, habits in categories.items():
            print(f"\nCategory: {category}")
            for habit in habits:
                print(f"    Title: {habit.title}, Streak: {habit.streak}")

    def showCompletionRates(self):
        pass

    def showAnalytics(self):
        print("\n--- Longest Streak ---")
        self.calculateLongestStreakAll()
        print("\n--- Habits by Category ---")
        self.analyseByCategory()
        # print("\n--- Habits by Completion rate ---")
        # implement method that shows highest and lowest completion rates, or just lists them from highest to lowest.

class HabitTracker:
    def __init__(self):
        self.db = SQLiteDB()

    def createHabit(self, title, description, periodicity, category=None):
        habit = Habit(title, description, periodicity, category)
        habit_id = self.db.storeHabit(habit)
        print(f"Habit '{title}' created with ID: {habit_id}")

    def completeHabitTask(self, habit_id):
        habit = self.db.getHabit(habit_id)
        if habit:
            today = datetime.date.today()

            # Check if the habit was already completed today
            if habit.lastCompletionDate == today:
                print(f"Habit '{habit.title}' has already been completed today.")
                return

            # Complete the task
            habit.completeTask()
            self.db.storeCompletionRecord(habit_id, habit.lastCompletionDate)
            self.db.updateHabit(habit_id, habit)
            print(f"Habit '{habit.title}' marked as completed on {habit.lastCompletionDate}")
        else:
            print("Habit not found.")

    def _displayHabits(self, habits):
        """Helper method to display habits in a formatted way, including last completion date."""
        today = datetime.date.today()

        # Print a header row with proper alignment, including Last Completed
        print(f"{'ID':<8} {'Title':<24} {'Category':<24} {'Periodicity':<14} {'Streak':<8} {'Completion %':<14} {'Last Completed':<16}")
        print("-" * 108)  # Separator

        for habit_id, habit in habits:
            # Calculate total expected completions based on periodicity
            if habit.periodicity == 'daily':
                total_expected_completions = (today - habit.creationDate).days + 1
            elif habit.periodicity == 'weekly':
                total_expected_completions = ((today - habit.creationDate).days // 7) + 1

            # Total completions from the completion history
            total_completions = len(habit.completionHistory)

            # Calculate completion percentage
            completion_percentage = (total_completions / total_expected_completions) * 100

            # Format category and last completed date
            category = habit.category if habit.category else "No category"
            last_completed = habit.lastCompletionDate if habit.lastCompletionDate else "Never"

            # Print each habit's details with alignment
            print(f"{habit_id:<8} {habit.title:<24} {category:<24} {habit.periodicity:<14} {habit.streak:<8} {completion_percentage:<14.2f} {last_completed}")

    def listAllHabits(self):
        """Lists all habits with their details using the helper function."""
        habits = self.db.getAllHabits()
        self._displayHabits(habits)

    def filterHabitsByPeriodicity(self, periodicity):
        """Filter habits by periodicity and display them using the helper function."""
        habits = self.db.getHabitsByPeriodicity(periodicity)
        self._displayHabits(habits)

    def viewAnalytics(self):
        analytics = Analytics(self.db)
        analytics.showAnalytics()

    def editHabit(self, habit_id):
        habit = self.db.getHabit(habit_id)
        if habit:
            print(f"Editing habit: {habit.title}")
            print("Enter new values or press Enter to keep the current value.")

            new_title = input(f"Title ({habit.title}): ")
            new_description = input(f"Description ({habit.description if habit.description else 'None'}): ")

            # Enforce valid periodicity (either 'daily' or 'weekly') when editing
            while True:
                new_periodicity = input(f"Periodicity (daily/weekly) ({habit.periodicity}): ").lower()
                if new_periodicity in ['daily', 'weekly', '']:
                    break
                else:
                    print("Invalid input. Please enter 'daily' or 'weekly'.")

            new_category = input(f"Category ({habit.category if habit.category else 'None'}): ")

            # Update values if the user provided a new value
            habit.title = new_title if new_title else habit.title
            habit.description = new_description if new_description else habit.description
            habit.periodicity = new_periodicity if new_periodicity else habit.periodicity
            habit.category = new_category if new_category else habit.category

            self.db.updateHabit(habit_id, habit)
            print(f"Habit '{habit.title}' updated successfully!")
        else:
            print("Habit not found.")

    def deleteHabit(self, habit_id):
        habit = self.db.getHabit(habit_id)
        if habit:
            confirm = input(f"Are you sure you want to delete habit '{habit.title}'? (yes/no): ").lower()
            if confirm == 'yes':
                self.db.deleteHabit(habit_id)
                print(f"Habit '{habit.title}' has been deleted.")
            else:
                print("Deletion canceled.")
        else:
            print("Habit not found.")

    def listUncompletedHabitsToday(self):
        """Lists all habits that haven't been completed today"""
        habits = self.db.getAllHabits()
        today = datetime.date.today()

        uncompleted_habits = []  # Store uncompleted habits to print them later

        for habit_id, habit in habits:
            if habit.periodicity == 'daily' and habit.lastCompletionDate != today:
                category = habit.category if habit.category else "No category"
                last_completed = habit.lastCompletionDate if habit.lastCompletionDate else "Never"
                uncompleted_habits.append((habit_id, habit.title, category, habit.periodicity, last_completed))
            elif habit.periodicity == 'weekly':
                days_since_last_completion = (today - habit.lastCompletionDate).days if habit.lastCompletionDate else None
                if habit.lastCompletionDate is None or days_since_last_completion >= 7:
                    category = habit.category if habit.category else "No category"
                    last_completed = habit.lastCompletionDate if habit.lastCompletionDate else "Never"
                    uncompleted_habits.append((habit_id, habit.title, category, habit.periodicity, last_completed))

        if uncompleted_habits:
            # Print header
            print(f"{'ID':<8} {'Title':<24} {'Category':<24} {'Periodicity':<14} {'Last Completed':<16}")
            print("-" * 90)

            for habit in uncompleted_habits:
                habit_id, title, category, periodicity, last_completed = habit
                print(f"{habit_id:<8} {title:<24} {category:<24} {periodicity:<14} {last_completed}")
        else:
            print("All habits have been completed for today!")

    def clearDatabase(self):
        confirm = input("Are you sure you want to clear the entire database? This action cannot be undone. (yes/no): ").lower()
        if confirm == 'yes':
            self.db.clearTables()
            print("Database cleared successfully.")
        else:
            print("Action canceled.")

    def close(self):
        self.db.close()


def main():
    tracker = HabitTracker()
    while True:
        print("\n--- Habit Tracker ---")
        print("1. Create a new habit")
        print("2. Complete a habit task")
        print("3. List all habits")
        print("4. View analytics")
        print("5. Edit a habit")
        print("6. Delete a habit")
        print("7. List uncompleted habits for today")
        print("8. Clear database")
        print("9. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            title = input("Enter habit title: ")
            description = input("Enter habit description (optional): ")

            # Enforce valid periodicity (either 'daily' or 'weekly')
            while True:
                periodicity = input("Enter periodicity (daily/weekly): ").lower()
                if periodicity in ['daily', 'weekly']:
                    break
                else:
                    print("Invalid input. Please enter 'daily' or 'weekly'.")

            category = input("Enter category (optional): ")
            tracker.createHabit(title, description, periodicity, category)

        elif choice == '2':
            habit_id = int(input("Enter habit ID to complete: "))
            tracker.completeHabitTask(habit_id)

        elif choice == '3':
            periodicity = input("Filter by periodicity (daily/weekly) or press Enter to list all: ").lower()
            
            # Check if the user wants to filter by periodicity
            if periodicity in ['daily', 'weekly']:
                tracker.filterHabitsByPeriodicity(periodicity)
            else:
                # If no filter is provided, list all habits
                tracker.listAllHabits()


        elif choice == '4':
            tracker.viewAnalytics()

        elif choice == '5':
            habit_id = int(input("Enter habit ID to edit: "))
            tracker.editHabit(habit_id)

        elif choice == '6':
            habit_id = int(input("Enter habit ID to delete: "))
            tracker.deleteHabit(habit_id)

        elif choice == '7':
            tracker.listUncompletedHabitsToday()

        elif choice == '8':
            tracker.clearDatabase()

        elif choice == '9':
            tracker.close()
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

