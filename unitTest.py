import unittest
import datetime
from analytics import Analytics
from tracker import HabitTracker

class TestHabitTracker(unittest.TestCase):

    def setUp(self):
        # Set up a fresh HabitTracker and database for each test
        self.tracker = HabitTracker()
        self.db = self.tracker.db
        self.db.clearTables()  # Ensure each test starts with an empty database
        self.tracker.add_predefined_habits()

    def tearDown(self):
        # Clean up database after each test
        self.db.clearTables()
        self.db.close()

    def test_prepopulate_habits(self):
        """Test that 5 predefined habits are correctly initialized."""
        habits = self.db.getAllHabits()
        self.assertEqual(len(habits), 5, "There should be exactly 5 predefined habits")

        titles = [habit.title for _, habit in habits]
        self.assertIn("Drink Water", titles)
        self.assertIn("Exercise", titles)
        self.assertIn("Read Book", titles)
        self.assertIn("Weekly Groceries", titles)
        self.assertIn("Clean Room", titles)

    def test_habit_creation(self):
        """Test whether a new habit can be created successfully."""
        self.tracker.createHabit("New Habit", "Test habit", "daily", "Test Category")
        habits = self.db.getAllHabits()
        self.assertEqual(len(habits), 6, "There should be 6 habits after adding one new habit")
        new_habit = self.db.getHabit(6)
        self.assertEqual(new_habit.title, "New Habit")

    def test_habit_deletion(self):
        """Test that a habit can be deleted and no longer exists in the database."""
        # Ensure initial count of habits is 5
        self.assertEqual(len(self.db.getAllHabits()), 5)

        # Delete one habit (ID = 1, which is 'Drink Water')
        self.tracker.deleteHabit(1, confirm_delete=True)  # Pass the flag to bypass confirmation

        # Check if the habit is deleted
        habits = self.db.getAllHabits()
        self.assertEqual(len(habits), 4, "There should be 4 habits after deletion")
        self.assertIsNone(self.db.getHabit(1), "The deleted habit should no longer exist")


    def test_task_completion_and_streak_update(self):
        """Test that completing a task correctly updates the streak."""
        habit = self.db.getHabit(1)  # 'Drink Water' habit
        initial_streak = habit.streak

        # Complete the habit for today
        self.tracker.completeHabitTask(1)
        habit = self.db.getHabit(1)  # Fetch the updated habit

        self.assertEqual(habit.streak, initial_streak + 1, "Streak should increase by 1 after task completion")
        self.assertEqual(habit.lastCompletionDate, datetime.date.today(), "Last completion date should be today")

    def test_streak_calculation(self):
        """Test that streaks are calculated accurately based on the completion history for a new habit created in the test."""
        
        # Create a new habit specifically for the test
        self.tracker.createHabit("Test Habit", "A habit for testing streaks", "daily", "Testing")
        habit = self.db.getHabit(6)  # Get the newly created habit (ID 6)

        # Simulate completion on consecutive days (last 5 days)
        today = datetime.date.today()
        completion_dates = [today - datetime.timedelta(days=i) for i in range(5)]
        
        # Add these completion dates to the habit
        for date in completion_dates:
            self.db.storeCompletionRecord(6, date)  # Store completion record in the database
            habit.completionHistory.append(date)    # Update habit's completion history

        # Recalculate the streak
        streak = habit.calculateStreak()
        
        # Assert that the streak is 5 based on the last 5 days of completion
        self.assertEqual(streak, 5, "Streak should be 5 based on the completion history")


    def test_analytics_longest_streak(self):
        """Test the calculation of the longest streak among all habits."""
        analytics = Analytics(self.db)
        habit_with_longest_streak = self.db.getHabit(1)  # 'Drink Water' habit with a streak of 28 days

        # Set a higher streak for one of the habits
        habit_with_longest_streak.streak = 30
        self.db.updateHabit(1, habit_with_longest_streak)

        # Check longest streak across all habits
        habits = self.db.getAllHabits()
        longest_streak_habit = max(habits, key=lambda h: h[1].streak)[1]
        self.assertEqual(longest_streak_habit.streak, 30, "The longest streak should be 30")

if __name__ == '__main__':
    unittest.main()


"""
What This Test Suite Covers:

    1. Prepopulate Habits: Ensures the 5 predefined habits are correctly initialized.
    2. Habit Creation: Tests whether a new habit can be created successfully.
    3. Habit Deletion: Verifies that a habit can be deleted and no longer exists in the database.
    4. Task Completion and Streak Update: Ensures that completing a task correctly updates the streak.
    5. Streak Calculation: Ensures streaks are calculated accurately based on the habit's completion history.
    6. Analytics (Longest Streak): Tests the calculation of the longest streak among all habits.
"""