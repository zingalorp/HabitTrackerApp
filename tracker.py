import datetime
from database import SQLiteDB
from habit import Habit
from analytics import Analytics

# Define the HabitTracker class for user interaction and CLI functionality
class HabitTracker:
    def __init__(self):
        self.db = SQLiteDB()
        self.add_predefined_habits()

    def add_predefined_habits(self):
        # Check if there are already habits in the database
        if self.db.getAllHabits():
            return  # Skip if habits already exist

        # Predefined habits
        predefined_habits = [
            {"title": "Drink Water", "description": "Drink 8 cups of water", "periodicity": "daily", "category": "Health"},
            {"title": "Exercise", "description": "Daily exercise for 30 minutes", "periodicity": "daily", "category": "Fitness"},
            {"title": "Read Book", "description": "Read at least 10 pages", "periodicity": "daily", "category": "Learning"},
            {"title": "Weekly Groceries", "description": "Do groceries every Saturday", "periodicity": "weekly", "category": "Chores"},
            {"title": "Clean Room", "description": "Clean room every weekend", "periodicity": "weekly", "category": "Chores"}
        ]

        # Store predefined habits
        habit_ids = []
        for habit_data in predefined_habits:
            habit = Habit(
                habit_data['title'], 
                habit_data['description'], 
                habit_data['periodicity'], 
                habit_data['category']
            )
            habit_id = self.db.storeHabit(habit)
            habit_ids.append(habit_id)

        # Add 4 weeks of completion data for each habit
        self.add_completion_data(habit_ids)

    def add_completion_data(self, habit_ids):
        # Simulate 4 weeks of data for daily and weekly habits
        today = datetime.date.today()

        for habit_id in habit_ids:
            habit = self.db.getHabit(habit_id)
            if habit.periodicity == "daily":
                # Complete the habit every day for 28 days, up to yesterday
                for i in range(1, 29):  # Start from 1 to exclude today
                    date = today - datetime.timedelta(days=i)
                    self.db.storeCompletionRecord(habit_id, date)
                    habit.completionHistory.append(date)
                # Set the last completion date to yesterday
                habit.lastCompletionDate = today - datetime.timedelta(days=1)
                habit.calculateStreak()  # Recalculate streak
                self.db.updateHabit(habit_id, habit)  # Store updated habit in the DB

            elif habit.periodicity == "weekly":
                # Complete the habit every 7 days for 4 weeks, up to the last week
                for i in range(1, 5):  # Start from 1 to exclude today
                    date = today - datetime.timedelta(weeks=i)
                    self.db.storeCompletionRecord(habit_id, date)
                    habit.completionHistory.append(date)
                # Set the last completion date to the most recent completed week
                habit.lastCompletionDate = today - datetime.timedelta(weeks=1)
                habit.calculateStreak()  # Recalculate streak
                self.db.updateHabit(habit_id, habit)  # Store updated habit in the DB


    def createHabit(self, title, description, periodicity, category=None):
        habit = Habit(title, description, periodicity, category)
        habit_id = self.db.storeHabit(habit)
        print(f"Habit '{title}' created with ID: {habit_id}")

    def completeHabitTask(self, habit_id):
        habit = self.db.getHabit(habit_id)
        if habit:
            today = datetime.date.today()
            if habit.lastCompletionDate == today:
                print(f"Habit '{habit.title}' has already been completed.")
                return
            habit.completeTask()
            self.db.storeCompletionRecord(habit_id, habit.lastCompletionDate)
            self.db.updateHabit(habit_id, habit)
            print(f"Habit '{habit.title}' marked as completed on {habit.lastCompletionDate}")
        else:
            print("Habit not found.")

    def _displayHabits(self, habits):
        print(f"{'ID':<8} {'Title':<24} {'Category':<24} {'Periodicity':<14} {'Streak':<8} {'Last Completed':<16}")
        print("-" * 90)

        for habit_id, habit in habits:
            # Update category and last completed date
            category = habit.category if habit.category else "No category"
            last_completed = habit.lastCompletionDate if habit.lastCompletionDate else "Never"

            # Print habit details
            print(f"{habit_id:<8} {habit.title:<24} {category:<24} {habit.periodicity:<14} {habit.streak:<8} {last_completed}")

    def listAllHabits(self):
        """Lists all habits with their details using the helper function."""
        habits = self.db.getAllHabits()
        self._displayHabits(habits)

    def filterHabitsByPeriodicity(self, periodicity):
        """Filter habits by periodicity and display them using the helper function"""
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

            habit.title = new_title if new_title else habit.title
            habit.description = new_description if new_description else habit.description
            habit.periodicity = new_periodicity if new_periodicity else habit.periodicity
            habit.category = new_category if new_category else habit.category

            self.db.updateHabit(habit_id, habit)
            print(f"Habit '{habit.title}' updated successfully!")
        else:
            print("Habit not found.")

    def deleteHabit(self, habit_id, confirm_delete=False):
        habit = self.db.getHabit(habit_id)
        if habit:
            if confirm_delete:
                # Bypass the confirmation for testing purposes
                self.db.deleteHabit(habit_id)
                print(f"Habit '{habit.title}' has been deleted.")
            else:
                confirm = input(f"Are you sure you want to delete habit '{habit.title}'? (yes/no): ").lower()
                if confirm == 'yes':
                    self.db.deleteHabit(habit_id)
                    print(f"Habit '{habit.title}' has been deleted.")
                else:
                    print("Deletion canceled.")
        else:
            print("Habit not found.")


    def listUncompletedHabitsToday(self):
        habits = self.db.getAllHabits()
        today = datetime.date.today()

        uncompleted_habits = []

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
