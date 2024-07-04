import tui.frames as frames
import datetime

class UserProfileFrame(frames.Frame):
    '''
    Frame to display user profiles to the viewer
    '''
    
    def __init__(self, frame_mgr, user_id, last_keyword=None, page=1):
        '''
        Initialization of the frame

        :param user_id: ID of user whose profile is to be displayed
        :param last_keyword: Used to distinguish which frame called UserProfileFrame so we can return to it later
        :param page: Used to scroll through recent tweets of user whose profile is displayed
        '''
        
        super().__init__(frame_mgr)
        
        self.user_id = user_id
        self.last_keyword = last_keyword
        self.page = page
    
    def render(self):
        '''
        Renders and displays total number of tweets, following, and followers
        Additionally, displays 3 most recent tweets which can be paged through
        '''

        # Query used to find user name of the specified user
        self.frame_mgr \
            .db \
            .cursor \
            .execute("SELECT DISTINCT usr, name FROM users WHERE usr = ?", (self.user_id,))
        
        user_name = self.frame_mgr.db.cursor.fetchone()[1]
        
        print(f"\nViewing the profile of {user_name}")


        # Query used to find the number of total tweets the user has
        self.frame_mgr \
            .db \
            .cursor \
            .execute("SELECT COUNT(DISTINCT tid) FROM tweets WHERE writer = ?", (self.user_id,))

        num_tweets = self.frame_mgr.db.cursor.fetchone()[0]
        
        print(f"Total tweets: {num_tweets}")


        # Query used to find the number of users the user is following
        self.frame_mgr \
            .db \
            .cursor \
            .execute("SELECT COUNT(DISTINCT flwee) FROM follows WHERE flwer = ?", (self.user_id,))
                
        following_count = self.frame_mgr.db.cursor.fetchone()[0]
        
        print(f"Following: {following_count} user(s)")


        # Query used to find the number of followers the user has
        self.frame_mgr \
            .db \
            .cursor \
            .execute("SELECT COUNT(DISTINCT flwer) FROM follows WHERE flwee = ?", (self.user_id,))
                
        follower_count = self.frame_mgr.db.cursor.fetchone()[0]
        
        print(f"Followers: {follower_count} user(s)")


        # Query used to find the users tweets
        self.frame_mgr \
            .db \
            .cursor \
            .execute("SELECT DISTINCT tid, text FROM tweets WHERE writer = ? ORDER BY tdate DESC LIMIT ?, 4", (self.user_id, (self.page-1) * 3))
        
        tweets = self.frame_mgr.db.cursor.fetchall()
        tweets_len = len(tweets)   # finds the length of the results (the number of tweets to display)

        
        print("\nUsers tweets:")
        
        # Displays users tweets
        for tweet in tweets[:3]:
            print(f"{tweet[1]}")
        
        # Notifies viewer if user has no tweets
        if tweets_len == 0:
            print("User has no tweets.")
        print()

        # Query for checking if the user can follow the user he is viewing
        self.frame_mgr \
            .db \
            .cursor \
            .execute("SELECT COUNT(DISTINCT flwer) FROM follows WHERE flwer = ? AND flwee = ?", (self.frame_mgr.db.user.id, self.user_id))
        
        can_follow = self.frame_mgr.db.cursor.fetchone()[0] == 0

        # Shows follow option only if the viewer is not viewing their own profile
        # and if the viewer does not follow the user already
        if self.user_id != self.frame_mgr.db.user.id:
            if can_follow:
                self.add_dynamic_render("Follow User", "FOLLOW")

        # If more than 3 tweets are returned from the query, displays the next page dynamic option to view additional tweets
        if tweets_len > 3:
            self.add_dynamic_render(f"Next Page -->", "NEXT")
        
        # If current page is not the first page, displays the previous page dynamic option
        if self.page != 1:
            self.add_dynamic_render(f"Prev Page <--", "PREV")

        # Displays the back to previous page option
        self.add_dynamic_render("Back", "BACK")

    def handle_dynamic_event(self, response):
        '''
        Handles user option selection and either moves user to the next/previous page
        of preview tweets, previous frame, or handles following the displayed user.
        
        :param response: Contains user option selection
        '''
        
        # Placed here by Nick (maodus) to save clock cycles
        if response not in self.dynamic_ids:
            return

        # Returns user to the previous frame if corresponding option is selected
        if self.dynamic_ids[response] == "BACK":

            if self.last_keyword:
                self.frame_mgr.display(frames.UserSearchFrame(self.frame_mgr, self.last_keyword))
            else:
                self.frame_mgr.display(frames.ListFollowersFrame(self.frame_mgr)) 
        
        # Displays next or previous set of search results if corresponding options are selected
        elif self.dynamic_ids[response] == "NEXT":
            self.frame_mgr.display(frames.UserProfileFrame(self.frame_mgr, self.user_id, self.last_keyword, self.page + 1))
        elif self.dynamic_ids[response] == "PREV":
            self.frame_mgr.display(frames.UserProfileFrame(self.frame_mgr, self.user_id, self.last_keyword, self.page - 1))
        
        # Handles following of user and refreshes user profile page
        elif self.dynamic_ids[response] == "FOLLOW":

            date_now = datetime.datetime.now()  # gets and stores the present date
            follow_date = date_now.strftime("%Y-%m-%d")  # converts present date into a string and stores it to ready for insertion query
            follow_data = (self.user_id, self.frame_mgr.db.user.id, follow_date)  # tuple to hold parameters for insertion query

            # Creates and inserts the user into the database
            self.frame_mgr \
            .db \
            .cursor \
            .execute('INSERT INTO follows (flwee, flwer, start_date) VALUES (?,?,?);', follow_data)

            self.frame_mgr.db.connection.commit()
            self.frame_mgr.display(frames.UserProfileFrame(self.frame_mgr, self.user_id, self.last_keyword, self.page))  # Refreshes page

            print("\nUser successfully followed!")
