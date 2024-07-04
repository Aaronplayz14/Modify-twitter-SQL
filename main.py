import sys
from tui.core import FrameManager, Database
from tui.frames import EntryFrame

if __name__ == "__main__":

    if len(sys.argv) != 1:
        db_path = sys.argv[1]  # stores the primary argument as the database path
    else:
        db_path = input("Please input a valid path to your selected database: ")
    
    db = Database()
    db.connect(db_path)

    frame_mgr = FrameManager(db) # Create frame manager instance
    frame_mgr.display(EntryFrame(frame_mgr)) # Display our entry frame

    while frame_mgr.shouldDisplay:
        # Handle user input for the frame
        usr_resp = input("\nPlease select an option: ")
        frame_mgr.process_input(usr_resp)