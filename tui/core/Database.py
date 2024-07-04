import sqlite3
import os.path

class Database:
    def __init__(self):
        '''
        Initializes the Database object. 

        self.connection and self.cursor are abstracted sqlite objects that are 
        used for interacting with the local db

        self.user will contain all the attributes of the currently logged in user.
        '''
        
        self.connection = None
        self.cursor = None
        self.user = None

    def connect(self, path):
        '''
        Connect the python sqlite library to the sql database.

        :param path: A path string to the file location of the database
        '''

        first_time = False  # variable used to check if the database presently exists
        
        # Checks if path exists, if not creates the database and clarifies that tables need to be defined
        if not os.path.exists(path):
            f = open(path, "w")
            f.close()
            first_time = True

        
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

        self.cursor.execute(' PRAGMA foreign_keys=ON; ')
        self.connection.commit()

        # If the database did not exist prior to running, define tables
        if first_time:
            self.define_tables()


    def define_tables(self):
        '''
        Create a db file with all the necessary tables for this project.
        '''

        queries = ''' 
            drop table if exists includes;
            drop table if exists lists;
            drop table if exists retweets;
            drop table if exists mentions;
            drop table if exists hashtags;
            drop table if exists tweets;
            drop table if exists follows;
            drop table if exists users;

            create table users (
            usr         int,
            pwd	      text,
            name        text,
            email       text,
            city        text,
            timezone    float,
            primary key (usr)
            );
            create table follows (
            flwer       int,
            flwee       int,
            start_date  date,
            primary key (flwer,flwee),
            foreign key (flwer) references users,
            foreign key (flwee) references users
            );
            create table tweets (
            tid	      int,
            writer      int,
            tdate       date,
            text        text,
            replyto     int,
            primary key (tid),
            foreign key (writer) references users,
            foreign key (replyto) references tweets
            );
            create table hashtags (
            term        text,
            primary key (term)
            );
            create table mentions (
            tid         int,
            term        text,
            primary key (tid,term),
            foreign key (tid) references tweets,
            foreign key (term) references hashtags
            );
            create table retweets (
            usr         int,
            tid         int,
            rdate       date,
            primary key (usr,tid),
            foreign key (usr) references users,
            foreign key (tid) references tweets
            );
            create table lists (
            lname        text,
            owner        int,
            primary key (lname),
            foreign key (owner) references users
            );
            create table includes (
            lname       text,
            member      int,
            primary key (lname,member),
            foreign key (lname) references lists,
            foreign key (member) references users
            );
        '''.strip().split(";")[:-1]  # get all queries seperately

        for query in queries:
            query = query.strip() + ";"  # clean up our query
            self.cursor.execute(query)

        self.connection.commit()