import tui.frames as frames

class ListFollowersFrame(frames.Frame):
    '''
    Frame used to display the list followers screen to the user
    '''
    
    def __init__(self, frame_mgr):
        '''
        Initialization of the frame
        '''
        
        super().__init__(frame_mgr)

        self.user = self.frame_mgr.db.user.id # self.user is set to the user currently logged in 

    def render(self):
        ''' 
        Displays all followers for the user currently logged in
        '''
        
        user_parameter = (self.user,)
        self.frame_mgr \
            .db \
            .cursor \
            .execute("SELECT flwer FROM follows WHERE flwee = ?;", user_parameter) # query for fetching all followers for the followee currently logged in 
        
        self.followers = self.frame_mgr.db.cursor.fetchall() # stores all followers in a list (used fetchall())
        
        print("\nAll followers:\n")

        # Iterates through the list of followers and renders each follower
        # with an selection index so the user can select followers to interact further
        for follower in self.followers:
            self.add_dynamic_render(follower[0]) 

        self.add_dynamic_render("Back", "BACK")  # adds the back page option to the dynamic options


    def handle_dynamic_event(self, response):
        '''
        Handles dynamic events to allow the user to interact with one of their followers and return to the LoggedIn/main page.

        :param response: Contains user option selection
        '''
        
        # Selects follower and displays frame for further profile interaction
        if response not in self.dynamic_ids:
            selected_flwer = self.followers[int(response) - 2][0]
            self.frame_mgr.display(frames.UserProfileFrame(self.frame_mgr, selected_flwer, None))
            return
        
        # Returns user to the LoggedInFrame/Home page if corresponding option is selected
        if self.dynamic_ids[response] == "BACK":
            self.frame_mgr.display(frames.LoggedInFrame(self.frame_mgr))
        
    
