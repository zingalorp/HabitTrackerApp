# HabitTrackerApp

## Overview

This is a Python-based command-line habit tracking application that allows users to manage daily and weekly habits. The app helps users create habits, track progress, and analyse their completion rates, using an SQLite database for persistence. The tracker opens with 5 predefined habits with 4 weeks of completion data, for testing purposes. Additionally, the app includes a unit test suite to ensure that the main features work properly.

## Features

- Add, edit, and delete habits.
- Track habits based on periodicity (daily or weekly).
- View completion history and streaks.
- Analyse habits by category and completion rates.
- Store data using SQLite database.
- Predefined habits and data for testing.

## How to Use

1. **Clone the repository**:
   ```bash
   git clone https://github.com/zingalorp/HabitTrackerApp.git
   cd HabitTrackerApp

2. **Run the app**: Run the following command in your terminal:
    ```bash
    python main.py

3. **Main Menu Options:**  
	- Create a habit  
	- Complete a habit task  
	- List all habits  
	- View analytics  
	- Edit a habit  
	- Delete a habit  
	- List uncompleted habits for today  
	- Clear database (use with caution)  
	- Exit  

4. **Running Unit Tests**: Run the unit tests to verify functionality using:
   ```bash
   python unitTest.py

5. **File Structure**:
   - analytics.py: Contains the Analytics class responsible for calculating streaks, completion rates, and category-based analysis.
   - habit.py: Contains the Habit class representing individual habits with methods for task completion and streak calculation.
   - database.py: Contains the SQLiteDB class that handles database operations like storing and retrieving habit data.
   - tracker.py: Contains the HabitTracker class responsible for user interaction and command-line interface functionality
   - main.py: The entry point for running the application.
   - unitTest.py: The test suite for unit testing the habit tracker funcionality.

## Dependencies

- Python 3.x
- SQLite (comes bundled with Python)

## GitHub Link
https://github.com/zingalorp/HabitTrackerApp
