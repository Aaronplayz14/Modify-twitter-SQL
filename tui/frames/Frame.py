class Frame:
    '''
    An abstract class in which sub-frames can inherit from to gain full frame functionality that is recognizable by the FrameManager.
    '''

    def __init__(self, frame_mgr):
        '''
        Initialization of the frame
        '''
        
        self.frame_mgr = frame_mgr

        # Static options are a collection of the possible options given to the user that are always present
        self.static_options = {}

        # Dynamic_ids are the option numbers for options that are more dynamic
        # Such as a specific tweet being displayed as opposed to the log out button
        self.dynamic_ids = {}

        # Tracks number of dynamic options displayed
        self._dynamic_size = 0  
    
    def render(self):
        '''
        Renders all of the designated static display options and associated text
        '''
        
        if len(self.static_options) > 0:
            for i, option in self.static_options.items():
                print(f'{i}) {option["text"]}')
        
    def handle_event(self, response):
        '''
        Handles input for all display options

        :param response: The input provided by the user
        '''
        
        statics_len = len(self.static_options)
        

        # Handle input for all static options if present
        if statics_len > 0 and response in self.static_options:
            self.static_options[response]["handler"]()

        elif response.isnumeric() and (statics_len < int(response) <= statics_len + self._dynamic_size):
            self.handle_dynamic_event(response)
            
        else:
             print("Sorry, invalid input. Please try again")

    def add_dynamic_render(self, option_text, id = None):
        '''
        Renders a new dynamic option

        :param option_text: The text to be displayed next to the option number
        '''
        
        self._dynamic_size += 1  # increases option selection number of new dynamic option 
        opt_index = self._dynamic_size + len(self.static_options)  # sets new opt_index to one after the previous dynamic option

        # Set ID for dynamic option
        if id != None:
            self.dynamic_ids[str(opt_index)] = id

        print(f'{opt_index}) {option_text}')  # displays option index and corresponding descriptor text

    def handle_dynamic_event(self, response):
        '''
        Handles input for all dynamic display options,
        presently used to instantiate this function as it is used amongst all inheriting classes

        :param response: Contains user option selection
        '''
        
        pass