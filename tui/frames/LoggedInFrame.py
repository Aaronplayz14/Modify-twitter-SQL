import tui.frames as frames

class LoggedInFrame(frames.Frame):
    '''
    Frame used to display the logged in screen (referred to as the main or home page)
    '''
    
    def __init__(self, frame_mgr, page=1):
        '''
        Initialization of the frame
        
        :param page: Integer storing the page of tweets being viewed on the main page
        '''
        
        super().__init__(frame_mgr)

        self.page = page
        self.query_results = []
        self.result_size = 0
        
        # Static options are a collection of the possible options given to the user that are always present on this given frame
        self.static_options = {
            "1": {
                "text": "Write Tweet",
                "handler": self.__handle_tweet
            },

            "2": {
                "text": "Search for Tweets",
                "handler": self.__handle_searchtweet
            },
            
            "3": {
                "text": "Search User",
                "handler": self.__handle_user_search
            },
            
            "4": {
                "text": "Display Followers",
                "handler": self.__handle_display_followers
            }
          
        }

    def render(self):
        '''
        Renders and displays all static options and dynamic options. 
        Also, finds and displays the tweets and retweets from the users the logged in user is following.
        '''
        
        print(f"\nYou are now logged in as: {self.frame_mgr.db.user.name} \n")
        super().render()
        
        # Query to find all tweets and retweets from the users the logged in user is following
        self.frame_mgr \
            .db \
            .cursor \
            .execute(f'''
                    SELECT DISTINCT t.tid, t.text, t.tdate, t.writer
                    FROM tweets t
                    JOIN follows f on f.flwer = ?
                    LEFT JOIN retweets r ON t.tid = r.tid
                    WHERE t.writer = f.flwee
                    OR f.flwee = r.usr
                    ORDER BY COALESCE(r.rdate, t.tdate) DESC
                    LIMIT ?, 6;
                ''', (self.frame_mgr.db.user.id, (self.page - 1) * 5))
        
        self.query_results = self.frame_mgr.db.cursor.fetchall() # stores the query results 
        self.result_len = len(self.query_results)  # finds the length of the results (the number of tweets/retweets to display)
        
        # Prints funny header if the user has no tweets in their home page
        if self.result_len == 0:
            print("\nNo Tweets! Go make some friends!")
        
        # Renders and displays tweets and retweets
        elif self.result_len >=1:
            print(f"\n   {'tID':^15}| {'Date':^10} | {'Writer':^16} | Tweet")
            print()
        
        for result in self.query_results[:5]:
            self.add_dynamic_render(f"{result[0]:^15}| {result[2]:10} | {result[3]:^16} | {result[1]}")
        
        print()  # buffer for output cleanliness

        # If more than 5 tweets are returned from the query, displays the next page dynamic option to view additional tweets
        if self.result_len > 5:
            self.add_dynamic_render(f"Next Page -->", "NEXT")
        
        # If current page is not the first page, displays the previous page dynamic option
        if self.page != 1:
            self.add_dynamic_render(f"Prev Page <--", "PREV")
        
        print()

        # Displays log out dynamic option
        self.add_dynamic_render(f"Log out", "LOGOUT")

        
    def handle_dynamic_event(self, response):
        '''
        Handles user option selection and either moves user to the next/previous page
        of home page tweets, or displays a frame corresponding to the users desired action.
        
        :param response: Contains user option selection
        '''
        
        # Selects the desired tweet on home page and displays frame for further tweet interaction
        if response not in self.dynamic_ids:
            selected_twt = self.query_results[int(response) - len(self.static_options) - 1][0]
            self.frame_mgr.display(frames.ViewTweetFrame(self.frame_mgr, selected_twt))
            return
        
        # Displays next or previous set of home page tweets if corresponding options are selected
        if self.dynamic_ids[response] == "NEXT":
            self.frame_mgr.display(frames.LoggedInFrame(self.frame_mgr, self.page + 1))
        elif self.dynamic_ids[response] == "PREV": 
            self.frame_mgr.display(frames.LoggedInFrame(self.frame_mgr, self.page - 1))
        
        # Returns user to the login/register page if corresponding option is selected
        elif self.dynamic_ids[response] == "LOGOUT": 
            self.__handle_logout()
        

    def __handle_logout(self):
        '''
        Handles logging out current user
        '''
        
        self.frame_mgr.db.user = None  # "log out"
        self.frame_mgr.display(frames.EntryFrame(self.frame_mgr))

    def __handle_user_search(self):
        '''
        Intakes user search keyword and displays corresponding frame
        '''
        
        keyword = input("What user would you like to search for? ")
        self.frame_mgr.display(frames.UserSearchFrame(self.frame_mgr, keyword))
        
    def __handle_tweet(self):
        '''
        Intakes desired tweet text and displays corresponding frame
        '''
        
        tweet_text = input("Please input the text for your tweet: ")
        self.frame_mgr.display(frames.ComposeTweetFrame(self.frame_mgr, tweet_text))
    
    def __handle_searchtweet(self):
        '''
        Intakes tweet search keywords and displays corresponding frame
        '''
        
        # Checks if user has inputted any keywords
        valid_keywords = False
        
        while not valid_keywords:
            
            searchtweet_keywords = input("Please input the keywords you would like to search for: ")
            
            if searchtweet_keywords:
                valid_keywords = True
            else:
                print("\nPlease enter a valid search!\n")
        
        self.frame_mgr.display(frames.SearchForTweetFrame(self.frame_mgr, searchtweet_keywords))  # displays tweet search results frame for further interaction

    def __handle_display_followers(self):
        '''
        Displays user's follower list frame 
        '''

        self.frame_mgr.display(frames.ListFollowersFrame(self.frame_mgr))

       