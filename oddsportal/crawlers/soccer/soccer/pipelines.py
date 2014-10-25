from sqlalchemy.orm import sessionmaker
from models import Result, db_connect, create_deals_table


class ResultsItem(object):
    """Livingsocial pipeline for storing scraped items in the database"""
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates results table.
        """
        engine = db_connect()
        create_deals_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """Save results in the database.

        This method is called for every item pipeline component.

        """
        session = self.Session()
        deal = Result(**item)

        try:
            session.add(deal)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item