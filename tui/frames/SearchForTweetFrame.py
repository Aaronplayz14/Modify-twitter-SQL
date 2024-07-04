import tui.frames as frames
import tui.utils.StringUtils as StringUtils

class SearchForTweetFrame(frames.Frame):
    '''
    Frame used to display tweet search results to the user
    '''
    
    def __init__(self, frame_mgr, keyword, page=1):
        '''
        Initialization of the frame

        :param keyword: String of keywords to search for 
        :param page: Integer representing page of search results to display
        '''
        
        super().__init__(frame_mgr)

        self.keyword = keyword
        self.page = page
        self.search_results = []
        self.result_size = 0

    def render(self):
        '''
        Renders and displays tweet keyword search results and dynamic options
        '''
        
        print(f"\nTweet search results for: {self.keyword} \n")
        

        listKeyword = str(self.keyword).split()
        
        keyword_query = ''  # variable to hold the WHERE clause of the query for dynamic SQL query generation

        # Checking if the first keyword is a hashtag and assigning WHERE clause accordingly
        if listKeyword[0].startswith("#"):
            keyword_query = "WHERE (t.tid = m.tid AND (UPPER(m.term) = ?)) "
        else:
            keyword_query = "WHERE (UPPER(t.text) LIKE '%' || ? || '%') "

        # Traversing listkeyword and assigning OR statements for each keyword after first dependent on presence of hashtag
        if len(listKeyword) > 1:
            for i in range(1, len(listKeyword)):
                if listKeyword[i].startswith("#"):
                    keyword_query += "OR (t.tid = m.tid AND (UPPER(m.term) = ?)) "
                else:
                    keyword_query += "OR (UPPER(t.text) LIKE '%' || ? || '%' ) "
        
        # Turns hashtag keywords into alphanumeric only terms ready for query use
        for i in range(len(listKeyword)):
            if listKeyword[i].startswith("#"):
                listKeyword[i] = StringUtils.get_hashtags(listKeyword[i])[0]
        
        # Turns all keyword elements to UPPER to negate any case-sensitivity
        for i in range(len(listKeyword)):
            listKeyword[i] = listKeyword[i].upper()
        
        # Query to acquire all tweets related to search terms ordered by tweet date in an latest to oldest format
        self.frame_mgr \
            .db \
            .cursor \
            .execute(f'''
                    SELECT DISTINCT t.tid, t.text, t.tdate, t.writer
                    FROM tweets t LEFT JOIN mentions m on t.tid = m.tid
                    {keyword_query}
                    ORDER BY t.tdate DESC
                    LIMIT ?, 6;
                ''', (*listKeyword, (self.page - 1) * 5))
    

        self.search_results = self.frame_mgr.db.cursor.fetchall()  # stores the query results
        self.result_len = len(self.search_results)  # finds the length of the results (the number of tweets/retweets to display)
        
        # Displays output headers for tweets
        print(f"   {'tID':^15}| {'Date':^10} | {'Writer':^16} | Tweet")
        print("  ------------------------------------------")

        # Displays every queried tweet
        for result in self.search_results[:5]:
            self.add_dynamic_render(f"{result[0]:^15}| {result[2]:10} | {result[3]:^16} | {result[1]}")

        # If no tweets are found, notifies the user
        if self.result_len == 0:
            print("No results found.")
        
        print()  # buffer for output cleanliness
        
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
        of tweet search results, home page, or a specified tweet's details page for further interaction.
        
        :param response: Contains user option selection
        '''

        # Selects the desired tweet from search results and displays frame for further tweet interaction
        if response not in self.dynamic_ids:
            selected_twt = self.search_results[int(response) - 1][0]
            self.frame_mgr.display(frames.ViewTweetFrame(self.frame_mgr, selected_twt, self.keyword))# show more info of that tweet that been picked
            return
        
        # Displays next or previous set of search results if corresponding options are selected
        if self.dynamic_ids[response] == "NEXT":
            self.frame_mgr.display(frames.SearchForTweetFrame(self.frame_mgr, self.keyword, self.page + 1))
        elif self.dynamic_ids[response] == "PREV": 
            self.frame_mgr.display(frames.SearchForTweetFrame(self.frame_mgr, self.keyword, self.page - 1))
        
        # Returns user to the home page if corresponding option is selected
        elif self.dynamic_ids[response] == "BACK": 
            self.frame_mgr.display(frames.LoggedInFrame(self.frame_mgr))# go back to the main page
