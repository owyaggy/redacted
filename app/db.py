'''
This file contains methods that accesses and add to the database.
'''

import sqlite3

#initialize db file
DB_FILE = "database.db"

#connect db
db = sqlite3.connect(DB_FILE)
c = db.cursor()

#create tables for database
command = "CREATE TABLE IF NOT EXISTS "

# Creating table with username | password | stories contributed table
c.execute (command + "user_info (username TEXT, password TEXT, stories_contributed TEXT, CONSTRAINT uni_user UNIQUE(username))") # vals in username col must be unique

# creating table with story title | user contributed | story entry
c.execute (command + "story (title TEXT type UNIQUE, contributor TEXT, entry TEXT)")

def get_login(username, password):
    """
    Returns the correct error message when the user is logging in.

        Parameters:
            username (str): The username that the user entered
            password (str): The password that the user entered

        Returns:
            "User Not Found": Username does not match any entry in the database
            "Incorrect Password": Username is found in the database but password doesn't match
            "": Username and password matches

    """
    # avoid thread error
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    # check if username exists in the db
    command = f"SELECT * FROM user_info WHERE (username = \"{username}\")"
    c.execute(command)
    data = c.fetchall()

    # no user exists
    if(data == []):
        return "User Not Found"

    # password is wrong
    elif(data[0][1] != password):
        return "Incorrect Password"

    # username and password is correct
    else:
        return ""


def add_login(username, password):
    """
    Creates an account in the database
    Adds a new row for new username and password in user_info table in database

        Parameters:
            username (str): The username that the user entered
            password (str): The password that the user entered
    """

    # avoid thread error
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    # add username and password pair to database, no stories_contributed blank at account creation
    command = "INSERT INTO user_info VALUES(?, ?, ?)"
    c.execute(command, (username, password, ""))

    # commit changes to db
    db.commit()


def create_story(title, user, entry):
    """
    Add a story to the story table in database

        Parameters:
            title (str): The title of the story that the user entered
            user (str): The user that creates the story
            entry (str): The text that the user entered as the entry of the story
    """
    #avoid thread error
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    newtitle = title
    if " " in title:
        newtitle = title.replace(" ", "_")
    c.execute("INSERT INTO story VALUES(?,?,?)", (newtitle, user, entry))

    db.commit()

    add_stories_contributed(newtitle, user)



# add to existing stories kind of works for now
def add_to_story(title, contributor, entry):
    """
    add_to_story would add entries and contributors of the entry to story database
    also add this story to the list of stories that the user stories_contributed
    returns nothing

    As of now it would add to the story every time the command is called, re running won't
    clear the database
    """
    #avoid thread error
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    # creates a dictionary to facilitate argument passing in the future
    dict = {"title":title, "contributor":contributor, "entry": entry}

    # get the contributor and entry from the current story
    command = "SELECT contributor, entry FROM story WHERE title=:title"
    c.execute(command, dict) # the field in dict would replace :title
    contributor_entry_list = c.fetchall() #stores the information. It's a list of tuple, so kind of like 2D array


    # add new information to contributor and entry through string concatenation, separated with \n
    entry_dict = contributor_entry_list[0][1] + "\n" + entry
    contributor_dict = contributor_entry_list[0][0] + "\n" + contributor

    # reset the dictionary to contain the most recent information
    dict['contributor'] = contributor_dict
    dict['entry'] = entry_dict

    #updates the database with the new dictionary
    c.execute("UPDATE story SET contributor = :contributor WHERE title =:title", dict)
    c.execute("UPDATE story SET entry = :entry WHERE title =:title", dict)
    db.commit()

    add_stories_contributed(title, contributor)




def get_story_addable(username):
    """
    This would get the stories that the user did not contribute to,
    these are the stories that they can add to on the /add page
    """
    #avoid thread error
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    #titles of all stories, each title in a tuple
    c.execute("SELECT title FROM story")
    titles = c.fetchall()

    stories_contributed = get_stories_contributed(username)

    #for testing
    #stories_contributed = ["story1"]

    addable_stories = []

    #if a story is not in stories_contributed, it's addable
    for i in titles:
        if ((i[0] in stories_contributed) == False):
            addable_stories.append(i[0])

    return addable_stories


def get_story (title):
    """
    get_story gets the entire story, returns the story entries and the different
    users that contributed to each entry in a list
    [titile, contributors_list, story_entry_list]
    Yuqing will code this part but Rachel should check since she's using it for the
    past story part in /home page
    """
    #avoid thread error
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    #selects contributors and entry
    c.execute("SELECT contributor, entry FROM story WHERE title = :title", {"title":title})
    entry_list = c.fetchall()
    output_list = [title]
    print(entry_list)
    #index 0 because tuple
    for i in range(2):
        #split for each \n
        if(entry_list != []):
            output_list.append(entry_list[0][i].split('\n'))

    #diag print statement
    #print(output_list)
    #print(get_story.__doc__)
    return output_list


def get_story_last_entry (title):
    """
    get_story_last_entry gets the last entry for a story, returns
    the user contributed to the last entry and the last entry in a list
    [contributor, last_entry]
    """
    #avoid thread error
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    # use get_story in its implementation
    output_list = []
    big_list = get_story(title)
    for i in range(2):
    	# [TITLE, [CONTRIBUTOR LIST], [ENTRY LIST]]
        print(big_list)
        output_list.append(big_list[i+1][-1])
    return output_list

def add_stories_contributed(title, contributor):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT stories_contributed FROM user_info WHERE username =:contributor", {"contributor": contributor})
    a = c.fetchall()

    if(a[0][0] != ""):
        stories_contributed = a[0][0] + "\n" + title
    else:
        stories_contributed = title

    dict = {"stories_contributed":stories_contributed, "contributor":contributor}

    c.execute("UPDATE user_info SET stories_contributed =:stories_contributed WHERE username = :contributor", dict)

    #c.execute("SELECT stories_contributed FROM user_info WHERE username =:contributor", {"contributor": contributor})

    db.commit()

def get_stories_contributed(username):
    """
    get_stories_contributed would return the list of stories that
    the user contributed
    Rachel will do this and determine what exactly it returns, whether it's the
    titles and then call get_story or the entire thing is ready for flask
    """
    #avoid thread error
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    c.execute("SELECT stories_contributed FROM user_info WHERE username =:username", {"username": username})
    list = c.fetchall()[0][0].split("\n")
    return list
