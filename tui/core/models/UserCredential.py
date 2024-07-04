class UserCredential:
    '''
    Stores user credentials so we can ask and recall variables when signing up users.
    '''
    
    def __init__(self, usr, pwd, name, email, city, timezone):
        self.id = usr
        self.password = pwd
        self.name = name
        self.email = email
        self.city = city
        self.timezone = timezone
