import tui.frames as frames
import datetime

class ViewTweetFrame(frames.Frame):
    '''
    Frame to display tweet details to the user
    '''

    def __init__(self, frame_mgr, tweet_id, keyword=None):
        '''
        Initialization of the frame

        :param tweet_id: The ID of the tweet being added
        :param keyword: Used to distinguish which frame called ViewTweetFrame so we can return to it later
        '''
        
        super().__init__(frame_mgr)
        
        self.keyword = keyword
        self.tid = tweet_id


    def render(self):
        '''
        Renders and displays tweet details, as well as number of replies and retweets.
        Additionally, renders and displays dynamic options to reply to and retweet the tweet being viewed.
        '''
        
        # Query to find tweet details of a given tweet
        self.frame_mgr \
            .db \
            .cursor \
            .execute(f'''
                    SELECT DISTINCT t.tid, t.text, t.tdate, t.writer
                    FROM tweets t
                    WHERE t.tid = ?
                ''', (self.tid,))
        
        self.tweetdetails = self.frame_mgr.db.cursor.fetchone()

        # Query to find number of replies this tweet has
        self.frame_mgr \
            .db \
            .cursor \
            .execute(f'''
                    SELECT COUNT(DISTINCT t.tid)
                    FROM tweets t
                    WHERE t.replyto = ?
                ''', (self.tid,))
        
        self.tweetreplycount = self.frame_mgr.db.cursor.fetchone()

        # Query to find number of retweets this tweet has
        self.frame_mgr \
            .db \
            .cursor \
            .execute(f'''
                    SELECT COUNT(DISTINCT r.usr)
                    FROM retweets r
                    WHERE r.tid = ?
                ''', (self.tid,))
        
        self.tweetrtcount = self.frame_mgr.db.cursor.fetchone()

        # Displays tweet information and details
        print(f"\n   Tweet ID: {self.tweetdetails[0]} | Date: {self.tweetdetails[2]} | Writer: {self.tweetdetails[3]} | {self.tweetdetails[1]}\n")
        print(f"   This tweet has {self.tweetreplycount[0]} replies and {self.tweetrtcount[0]} retweets!\n")

        # Displays reply option
        self.add_dynamic_render(f"Compose a reply", "REPLY")

        # Query to check if the user has retweeted this tweet already
        self.frame_mgr \
            .db \
            .cursor \
            .execute(f'''
                    SELECT COUNT(DISTINCT r.usr)
                    FROM retweets r
                    WHERE r.tid = ? AND r.usr = ?
                ''', (self.tid, self.frame_mgr.db.user.id))
        
        self.tweetrtcheck = self.frame_mgr.db.cursor.fetchone()

        # Shows retweet option only if the viewer has not retweeted this tweet already
        if self.tweetrtcheck[0] == 0:
            self.add_dynamic_render(f"Retweet this tweet", "RETWEET")
        
        # Displays the back to previous page option
        self.add_dynamic_render(f"Back", "BACK")


    def handle_dynamic_event(self, response):
        '''
        Handles user option selection and either moves user to previous frame,
        handles reply frame displaying, or handles retweet creation and insertion.
        
        :param response: Contains user option selection
        '''
        
        # Returns user to the previous frame if corresponding option is selected
        if self.keyword != None:
            if self.dynamic_ids[response] == "BACK": 
                self.frame_mgr.display(frames.SearchForTweetFrame(self.frame_mgr, self.keyword))
        else:
            if self.dynamic_ids[response] == "BACK": 
                self.frame_mgr.display(frames.LoggedInFrame(self.frame_mgr))
        
        # Prompts user for reply tweet text and displays frame for further tweet posting
        if self.dynamic_ids[response] == "REPLY": 
            reply_text = input("Please input the text for your reply: ")
            self.frame_mgr.display(frames.ComposeTweetFrame(self.frame_mgr, reply_text, self.tid))
        
        # Handles following of user and refreshes view tweet page
        elif self.dynamic_ids[response] == "RETWEET":

            date_now = datetime.datetime.now()  # gets and stores the present date
            retweet_date = date_now.strftime("%Y-%m-%d")  # converts present date into a string and stores it to ready for insertion query
            retweet = (self.frame_mgr.db.user.id, self.tid, retweet_date)  # tuple to hold parameters for insertion query
            
            # Creates and inserts the retweet into the database
            self.frame_mgr \
            .db \
            .cursor \
            .execute("INSERT INTO retweets (usr,tid,rdate) VALUES (?,?,?);", retweet)

            self.frame_mgr.db.connection.commit()

            print("\nThis tweet has been retweeted!")
            self.frame_mgr.display(frames.ViewTweetFrame(self.frame_mgr, self.tid, self.keyword))  # refreshes page
            

        
