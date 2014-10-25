import sys, os
sys.dont_write_bytecode = True

root_path = os.path.abspath(__name__).split('oddsportal')[0]
sys.path.append(root_path + 'oddsportal/')

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import models


def start():

    try:
        os.remove('../tmp/missing_games.txt')
    except:
        pass

    missing_games_writer = open('../tmp/missing_games.txt', 'a+')

    Session = sessionmaker()
    engine  = create_engine('postgresql://soccer:soccer@localhost/soccer_db')
    Session.configure(bind = engine)
    session = Session()
    session._model_changes = {}

    links = open(root_path + 'oddsportal/oddsportal/crawlers/soccer/present.log').readlines()

    for link in links[100]:
        
        print link
        tournament_url = link.split(' ')[3]
        check = session.query(models.Result).filter_by(tournament_url = tournament_url).all()

        if check:
            continue
        else:
            missing_games_writer.write(tournament_url)
            

if __name__ == "__main__":
    start()