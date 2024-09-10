from database import DB_conn
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from typing import Tuple

class SeasonManager:
    """
    It checks if the current season is over in order to
    create a new one.
    """

    def __init__(self):
        self.db_conn = DB_conn(dbname="budgetplanner")
    
    def create_new_season(self):
        """
        Create a new row for the table seasons in case of the 
        current season is over.
        """
        c_season = self._current_season() # (sid: int, start: date, finish: date)
        end_date = c_season[-1]
        if self._is_over(end_date):
            year, month = end_date.year, end_date.month
            sid = f"{year}{year%100 + 1}"
            start = date(year, month + 1, 1)
            finish = start + relativedelta(years=1) - relativedelta(days=1)
            self.db_conn.execute(f"INSERT INTO seasons (sid, start, finish)\
                                   VALUES ({sid}, '{start}', '{finish}')")
    
    def _current_season(self) -> Tuple[int, date, date]:
        """
        Recover the row of the current season
        """
        c_season = self.db_conn.execute("SELECT *\
                                         FROM seasons\
                                         ORDER BY sid DESC\
                                         LIMIT 1")
        return c_season[0]
    
    def _is_over(self, end_date: datetime.date) -> bool:
        """
        It checks if the current season is over.
        """
        current_date = datetime.now().date()
        return current_date > end_date


if __name__ == "__main__":
    s_manager = SeasonManager()
    s_manager.create_new_season()
