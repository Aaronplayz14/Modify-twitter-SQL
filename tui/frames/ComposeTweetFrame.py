import tui.frames as frames
import datetime
import tui.utils.StringUtils as StringUtils

class ComposeTweetFrame(frames.Frame):
    '''
    Frame used to display the compose tweet screen to the user
    '''
    
    def __init__(self, frame_mgr, tweet_text, reply=None):
        '''
        Initialization of the Frame

        :param frame_mgr: References the frame manager to make frame swapping easier
        :param tweet_text: String representing the text the user wants to tweet
        :param reply: Used to reference the tid of the post being replied to
        '''
        
        super().__init__(frame_mgr)

        self.tweet_text = tweet_text
        self.reply = reply

        # Static options are a collection of the possible options given to the user that are always present
        self.static_options = {
            "1": {
                "text": "Yes",
                "handler": self.__handle_compose
            },

            "2": {
                "text": "No",
                "handler": self.__handle_delete
            }
        }

    def render(self):
        '''
        Asks user to confirm the composing of the tweet and renders static options
        '''
        
        print("\nAre you sure you would like to compose the following tweet:")
        print(self.tweet_text + "\n")
        
        super().render()  # this call renders the static options to the user

    def __handle_compose(self):
        '''
        Handles the actual creation, insertion and storage of the tweet into the database 
        '''

        user_id = self.frame_mgr.db.user.id
        
        # For generating a unique tweet id
        self.frame_mgr \
            .db \
            .cursor \
            .execute("SELECT COUNT(*) FROM tweets;")
        
        tid = self.frame_mgr.db.cursor.fetchone()[0]  # fetches count which represents tweet id
        
        date_now = datetime.datetime.now()  # gets and stores the present date
        tweet_date = date_now.strftime("%Y-%m-%d")  # converts present date into a string and stores it to ready for insertion query
        
        tweet = (tid, user_id, tweet_date, self.tweet_text, self.reply)  # tuple to hold parameters for insertion query
        
        # Creates and inserts the tweet into the database
        self.frame_mgr \
            .db \
            .cursor \
            .execute("INSERT INTO tweets (tid,writer,tdate,text,replyto) VALUES (?,?,?,?,?);", tweet)
        
        self.frame_mgr.db.connection.commit()

        # Acquires all the hashtags in the tweet
        hashtags = StringUtils.get_hashtags(self.tweet_text)

        # Inserts all hashtags into respective tables and links to tweets
        for term in hashtags:
            # Get hashtag count
            self.frame_mgr \
                .db \
                .cursor \
                .execute("SELECT COUNT(*) FROM hashtags WHERE UPPER(term) = ?;", (term.upper(),))
            hashtag_exists = self.frame_mgr.db.cursor.fetchone()[0] != 0
            
            # Make sure not to add duplicate hashtags
            if not hashtag_exists:
                self.frame_mgr \
                    .db \
                    .cursor \
                    .execute("INSERT INTO hashtags (term) VALUES (?);", (term,))
                self.frame_mgr.db.connection.commit()

            # Insert into mentions
            self.frame_mgr \
                .db \
                .cursor \
                .execute("INSERT INTO mentions (tid,term) VALUES (?,?);", (tid, term))
            self.frame_mgr.db.connection.commit()

        print("\nSuccessfully tweeted!")
        self.frame_mgr.display(frames.LoggedInFrame(self.frame_mgr))  # returns to main page once tweet has passed

    def __handle_delete(self):
        self.frame_mgr.display(frames.LoggedInFrame(self.frame_mgr))  # returns to main page and drafted tweet is 'deleted'

