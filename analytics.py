import datetime

# Define the Analytics class for habit analysis
class Analytics:
    def __init__(self, db):
        self.db = db

    def calculateLongestStreakAll(self):
        """Show all habits with the highest streak for daily and weekly habits."""
        habits = self.db.getAllHabits()

        # Separate lists to store the highest streak habits for daily and weekly
        max_daily_streak = 0
        max_daily_habits = []

        max_weekly_streak = 0
        max_weekly_habits = []

        for habit_id, habit in habits:
            if habit.periodicity == 'daily':
                # Check if this habit has a higher streak than the current max_daily_streak
                if habit.streak > max_daily_streak:
                    max_daily_streak = habit.streak
                    max_daily_habits = [habit]  # Reset the list to this habit
                elif habit.streak == max_daily_streak:
                    max_daily_habits.append(habit)  # Add this habit to the list
            elif habit.periodicity == 'weekly':
                # Check if this habit has a higher streak than the current max_weekly_streak
                if habit.streak > max_weekly_streak:
                    max_weekly_streak = habit.streak
                    max_weekly_habits = [habit]  # Reset the list to this habit
                elif habit.streak == max_weekly_streak:
                    max_weekly_habits.append(habit)  # Add this habit to the list

        # Print out the habits with the highest streak for daily habits
        if max_daily_habits:
            print(f"\nLongest streak for daily habits: {max_daily_streak} days")
            for habit in max_daily_habits:
                print(f"  - Habit '{habit.title}' with a streak of {habit.streak} days")
        else:
            print("\nNo daily habits found.")

        # Print out the habits with the highest streak for weekly habits
        if max_weekly_habits:
            print(f"\nLongest streak for weekly habits: {max_weekly_streak} weeks")
            for habit in max_weekly_habits:
                print(f"  - Habit '{habit.title}' with a streak of {habit.streak} weeks")
        else:
            print("\nNo weekly habits found.")

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

    def calculateCompletionPercentage(self, habit):
        """Calculate and return the completion percentage for a habit using the first completion date."""
        today = datetime.date.today()

        # If there's no completion history, return 0% completion rate
        if not habit.completionHistory:
            return 0, 0, 0  # Return 0 for actual completions, expected completions, and percentage

        # Use the first completion date
        first_completion_date = min(habit.completionHistory)

        # Calculate total expected completions based on periodicity, starting from the first completion date
        if habit.periodicity == 'daily':
            total_expected_completions = (today - first_completion_date).days + 1
        elif habit.periodicity == 'weekly':
            total_expected_completions = ((today - first_completion_date).days // 7) + 1

        # Total completions from the completion history
        total_completions = len(habit.completionHistory)

        # Calculate completion percentage
        if total_expected_completions > 0:
            completion_percentage = (total_completions / total_expected_completions) * 100
        else:
            completion_percentage = 0

        return total_completions, total_expected_completions, completion_percentage

    def showCompletionRates(self):
        """Show the completion percentage for each habit sorted from highest to lowest."""
        habits = self.db.getAllHabits()
        completion_data = []

        # Gather the completion data for each habit
        for habit_id, habit in habits:
            total_completions, total_expected_completions, completion_percentage = self.calculateCompletionPercentage(habit)
            completion_data.append((habit.title, completion_percentage, total_completions, total_expected_completions))

        # Sort the list by completion percentage (index 1), in descending order
        completion_data.sort(key=lambda x: x[1], reverse=True)

        # Print the sorted completion rates
        for title, completion_percentage, total_completions, total_expected_completions in completion_data:
            print(f"Habit: {title}, Completion Rate: {completion_percentage:.2f}% "
                  f"(Actual: {total_completions}, Expected: {total_expected_completions})")

    def showAnalytics(self):
        print("\n--- Longest Streak ---")
        self.calculateLongestStreakAll()
        print("\n--- Habits by Category ---")
        self.analyseByCategory()
        print("\n--- Completion Rates (sorted by highest to lowest) ---\n")
        self.showCompletionRates()
