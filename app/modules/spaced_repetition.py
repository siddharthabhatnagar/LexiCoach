from datetime import datetime, timedelta

class SM2Scheduler:
    @staticmethod
    def next_interval(repetitions: int, ease_factor: float, quality: int) -> tuple[int, float]:
        if quality < 3:
            return 1, max(1.3, ease_factor - 0.2)
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = int((repetitions - 1) * ease_factor)
        ease_factor = max(1.3, ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        return interval, ease_factor

    @staticmethod
    def next_review_date(interval_days: int) -> datetime:
        return datetime.utcnow() + timedelta(days=interval_days)
