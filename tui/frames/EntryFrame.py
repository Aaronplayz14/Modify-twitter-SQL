from tui.core.models.UserCredential import UserCredential
import getpass
import tui.frames as frames

class EntryFrame(frames.Frame):
    '''
    Frame to display the login or register screen to the user
    '''
    
    def __init__(self, frame_mgr):
        '''
        Initialization of the frame
        '''
        
        super().__init__(frame_mgr)

        # Static options are a collection of the possible options given to the user that are always present
        self.static_options = {
            "1": {
                "text": "Login",
                "handler": self.__handle_login
            },

            "2": {
                "text": "Signup",
                "handler": self.__handle_signup
            },

            "3": {
                "text": "Exit",
                "handler": self.__handle_exit
            },
        }

    def render(self):
        '''
        Displays welcome message to user and renders static options
        '''
        
        print("\nHello and welcome to Twitter!\n")

        super().render()  # this call renders the static options to the user

    def __handle_exit(self):
        '''
        Handler for exiting the program.
        '''
        
        self.frame_mgr.shouldDisplay = False

    def __instantiate_user(self, user_data):
        '''
        Instantiates a new user into the local database.

        :param user_data: A tuple containing all necessary database-defined user attributes
        '''
        
        # Create our new user
        self.frame_mgr \
            .db \
            .cursor \
            .execute('INSERT INTO users (usr, pwd, name, email, city, timezone) VALUES (?,?,?,?,?,?);', user_data) 
        
        self.frame_mgr.db.connection.commit()

    def __handle_signup(self):
        '''
        Handler for registering users. This function will prompt the user with fields
        pertaining to the signup process and will take care of making sure the
        new user is added to the database with a unique id.
        '''

        city = input("Your city: ")
        timezone = input("Your timezone: ")
        name = input("Your name: ")
        email = input("Your email: ")
        password = getpass.getpass("Your password: ")  # hides the user's password from display

        # Error check for city. It can only be [A-Z] or [a-z] and contain spaces
        city_no_space = city.replace(" ", "")
        if not city_no_space.isalpha():
            print("\nCity can only contain the letters a-z along with spaces")
            self.frame_mgr.display(frames.EntryFrame(self.frame_mgr))
            return

        # Error check to make sure that timezone is a float
        try:
            int_time = float(timezone)
        except:
            print("\nTimezone must be a number")
            self.frame_mgr.display(frames.EntryFrame(self.frame_mgr))
            return

        # The next UNIQUE user id wil be the current user count
        self.frame_mgr \
            .db \
            .cursor \
            .execute("SELECT COUNT(*) FROM users;")
        
        # Data for our new user row
        id_offset = 1  # What we offset our user ids by
        user_id = self.frame_mgr.db.cursor.fetchone()[0] + id_offset
        user_data = (user_id, password, name, email, city, timezone)

        # Creates new user
        self.__instantiate_user(user_data)

        print(f"\nAccount successfully created with ID:{user_id}. Please login.")
        
        self.__handle_login()  # sends our user to the login screen when done


    def __attempt_login(self, login_data):
        '''
        Attempts to retrieve a user based on provided login information.

        :param login_data: A tuple containing the user's attempted login id and password
        
        :return: A tuple containing the number of users with matching login details
        and all database-defined details of said user.
        '''
        
        self.frame_mgr \
            .db \
            .cursor \
            .execute("SELECT COUNT(*), * FROM users WHERE usr = ? AND pwd = ?;", login_data)
        return self.frame_mgr.db.cursor.fetchone()


    def __handle_login(self):
        '''
        Handler for logging in. This function will prompt the user with fields
        pertaining to the login process.
        '''

        # Used to loop user id and password prompts until the user is logged in
        continue_loop = True
        login_result = None

        while continue_loop:
            user_id = input("\nYour user id: ")
            password = getpass.getpass("Your password: ")

            login_data = (user_id, password)

            # Query to see if our login credentials are correct
            login_result = self.__attempt_login(login_data)
            # [0]   -> COUNT(*)
            # [1:5] -> usr, pwd, name, email, city, timezone

            continue_loop = (not login_result[0])  # sets continue_loop to False if the user id and password are valid
            if (continue_loop and input("Invalid credentials, would you like to try again (y/n)? ") != 'y'):
                self.frame_mgr.display(frames.EntryFrame(self.frame_mgr))
                return
            
        self.frame_mgr.db.user = UserCredential(*login_result[1:])  # creates the user in memory in order to make referencing user credentials easier
        self.frame_mgr.display(frames.LoggedInFrame(self.frame_mgr))  # displays main menu frame