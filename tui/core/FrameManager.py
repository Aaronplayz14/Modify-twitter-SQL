
class FrameManager:
    '''
    A class that will be responsible for displaying the current frame and switching frames.
    ''' 

    def __init__(self, database):
        self.frame = None
        self.shouldDisplay = True
        self.db = database


    def display(self, frame):
        '''
        This function will set the current frame and display it.

        :param frame: The frame to activate and render.
        '''
        self.frame = frame
        self.frame.render()


    def process_input(self, response):
        '''
        This function will handover processing of input to the current active frame.

        :param response: A string containing the user's response.
        '''
        if self.frame:
            self.frame.handle_event(response)