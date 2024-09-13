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
        if self.lastCompletionDate != today:  # Only complete if not already done today
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
        self.streak = streak  # Ensure the streak is stored in the class variable
        return streak