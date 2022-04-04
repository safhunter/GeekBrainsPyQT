""" Server ORM classes """
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime


class ServerDB:
    Base = declarative_base()

    class AllUsers(Base):
        __tablename__ = 'all_users'
        id = Column(Integer, primary_key=True)
        username = Column(String, unique=True)
        last_conn = Column(DateTime)

        def __init__(self, login):
            self.username = login
            self.last_conn = datetime.datetime.now()

    class ActiveUsers(Base):
        __tablename__ = 'active_users'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('all_users.id'), unique=True)
        ip = Column(String)
        port = Column(Integer)
        time_conn = Column(DateTime)

        def __init__(self, user, ip_address, port, time_conn):
            self.user = user
            self.ip = ip_address
            self.port = port
            self.time_conn = time_conn

    class LoginHistory(Base):
        __tablename__ = 'login_history'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('all_users.id'))
        ip = Column(String)
        port = Column(Integer)
        last_conn = Column(DateTime)

        def __init__(self, user, ip, port, last_conn):
            self.user = user
            self.ip = ip
            self.port = port
            self.last_conn = last_conn

    def __init__(self, database_url='sqlite:///server_base.db3'):
        self.engine = create_engine(database_url, echo=False, pool_recycle=7200)
        self.session = None
        self.init_db()
        self.drop_active_users()

    def init_db(self):
        """ Init new database connection """
        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def reinit_db(self):
        """ Warning: Drop all data from tables!!! """
        self.Base.metadata.drop_all(self.engine)
        self.init_db()

    def drop_active_users(self):
        """ Delete all records in ActiveUsers table """
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port):
        """
            Executed when the user logs in, fixes the fact of login in the database
        :param username: Logged-in user
        :param ip_address: IP address of a user's connection
        :param port: IP port of a user's connection
        :return:
        """
        rez = self.session.query(self.AllUsers).filter_by(username=username)
        if rez.count():
            user = rez.first()
            user.last_conn = datetime.datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)

            self.session.commit()

        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)

        history = self.LoginHistory(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(history)

        self.session.commit()

    def user_logout(self, username):
        """ fixes the disconnection of the user 'username' """
        user = self.session.query(self.AllUsers).filter_by(username=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()

        self.session.commit()

    def users_list(self):
        """ Returns a list of known users with last login time.   """
        with self.session as session:
            result = session.query(
                self.AllUsers.username,
                self.AllUsers.last_conn,
            ).all()
        return result

    def active_users_list(self):
        """ Returns a list of active users """
        with self.session as session:
            result = session.query(
                self.AllUsers.username,
                self.ActiveUsers.ip,
                self.ActiveUsers.port,
                self.ActiveUsers.time_conn
            ).join(self.AllUsers).all()
        return result

    def login_history(self, username=None):
        """ Returns the login history for a user or for all users """
        with self.session as session:
            query = session.query(self.AllUsers.username,
                                       self.LoginHistory.last_conn,
                                       self.LoginHistory.ip,
                                       self.LoginHistory.port
                                       ).join(self.AllUsers)
            if username:
                query = query.filter(self.AllUsers.username == username)
            result = query.all()
        return result


if __name__ == '__main__':
    db = ServerDB('sqlite:///test_base.db3')
    db.reinit_db()
    db.user_login('client_1', '192.168.1.4', 8888)
    db.user_login('client_2', '192.168.1.5', 7777)
    # выводим список кортежей - активных пользователей
    print(db.active_users_list())
    # выполянем 'отключение' пользователя
    db.user_logout('client_1')
    user_lst = db.users_list()
    db.user_login('client_3', '192.168.1.6', 9999)
    print(f'user_lst: {user_lst}')
    # выводим список активных пользователей
    print(db.active_users_list())
    db.user_logout('client_2')
    print(db.users_list())
    print(db.active_users_list())

    # запрашиваем историю входов по пользователю
    # db.login_history('client_1')
    # # выводим список известных пользователей
    # print(db.users_list())
