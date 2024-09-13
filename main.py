from tracker import HabitTracker

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
        choice = input("Enter your choice (1-9): ")

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
            try:
                habit_id = int(input("Enter habit ID to complete: "))
                tracker.completeHabitTask(habit_id)
            except ValueError:
                print("Invalid input. Please enter a valid habit ID.")

        elif choice == '3':
            periodicity = input("Filter by periodicity (daily/weekly) or press Enter to list all: ").lower()
            
            # check if the user wants to filter by periodicity
            if periodicity in ['daily', 'weekly']:
                tracker.filterHabitsByPeriodicity(periodicity)
            else:
                # if no filter is provided, list all habits
                tracker.listAllHabits()

        elif choice == '4':
            tracker.viewAnalytics()

        elif choice == '5':
            try:
                habit_id = int(input("Enter habit ID to edit: "))
                tracker.editHabit(habit_id)
            except ValueError:
                print("Invalid input. Please enter a valid habit ID.")

        elif choice == '6':
            try:
                habit_id = int(input("Enter habit ID to delete: "))
                tracker.deleteHabit(habit_id)
            except ValueError:
                print("Invalid input. Please enter a valid habit ID.")

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


if __name__ == '__main__':
    main()
