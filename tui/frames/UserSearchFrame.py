import tui.frames as frames

class UserSearchFrame(frames.Frame):
    '''
    Frame to display user search results to the viewer
    '''
    
    def __init__(self, frame_mgr, keyword, page = 1):
        '''
        Initializaton to the frame

        :param keyword: Used to search for users
        :param page: Used to scroll through sets of users displayed
        '''
        
        super().__init__(frame_mgr)
        self.keyword = keyword
        self.page = page

        self.search_results = []
        self.result_size = 0

    def render(self):
        '''
        Renders and displays user keyword search results and dynamic options
        '''
        
        print(f"\nUser search results for: {self.keyword} \n")

        upper_keyword = self.keyword.upper()

        # We choose 6 rows here instead of 5 so we know when we have another page
        # The ORDER BY case statements will respectively:
        #   1. Give priority to matched names over matched cities
        #   2. Order matched cities by their length, and do the same for matched cities
        self.frame_mgr \
            .db \
            .cursor \
            .execute('''
                    SELECT DISTINCT u.usr, u.name, u.city 
                    FROM users u 
                    WHERE UPPER(u.name) LIKE '%' || ? || '%'
                    OR UPPER(u.city) LIKE '%' || ? || '%'
                    ORDER BY 
                    CASE WHEN UPPER(u.name) LIKE '%' || ? || '%' 
                        THEN 1
                        ELSE 2
                    END,
                    CASE WHEN UPPER(u.name) LIKE '%' || ? || '%' 
                        THEN LENGTH(u.name)
                        ELSE LENGTH(u.city)
                    END
                    LIMIT ?, 6;
                ''', (upper_keyword, upper_keyword, upper_keyword, upper_keyword, (self.page - 1) * 5))
        
        
        self.search_results = self.frame_mgr.db.cursor.fetchall()
        self.result_len = len(self.search_results)

        # Displays every queried user
        for result in self.search_results[:5]:
            self.add_dynamic_render(f"{result[1]} (from {result[2]})")

        if self.result_len == 0:
            print("No results found")

        print()
        
        # If more than 5 tweets are returned from the query, displays the next page dynamic option to view additional tweets
        if self.result_len > 5:
            self.add_dynamic_render(f"Next Page -->", "NEXT")
        
        # If current page is not the first page, displays the previous page dynamic option
        if self.page != 1:
            self.add_dynamic_render(f"Prev Page <--", "PREV")
        
        # Displays the back to previous page option
        self.add_dynamic_render(f"Back", "BACK")

    def handle_dynamic_event(self, response):
        '''
        Handles user option selection and either moves user to the next/previous page
        of user search results, home page, or a specified user's profile page for further interaction.
        
        :param response: Contains user option selection
        '''

        # Selects the desired user from search results and displays frame for further user interaction
        if response not in self.dynamic_ids:
            selected_user = self.search_results[int(response) - 1][0]
            self.frame_mgr.display(frames.UserProfileFrame(self.frame_mgr, selected_user, self.keyword))
            return

        # Displays next or previous set of search results if corresponding options are selected
        if self.dynamic_ids[response] == "NEXT":
            self.frame_mgr.display(frames.UserSearchFrame(self.frame_mgr, self.keyword, self.page + 1))
        elif self.dynamic_ids[response] == "PREV": 
            self.frame_mgr.display(frames.UserSearchFrame(self.frame_mgr, self.keyword, self.page - 1))

        # Returns user to the home page if corresponding option is selected
        elif self.dynamic_ids[response] == "BACK": 
            self.frame_mgr.display(frames.LoggedInFrame(self.frame_mgr))