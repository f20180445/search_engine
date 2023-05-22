# Importing BeautifulSoup class from the bs4 module
from bs4 import BeautifulSoup
import psycopg2
import os
import openai
# import wandb
from django.conf import settings
from dotenv import load_dotenv
from pandas import DataFrame

load_dotenv()

def parse_html():
    global usernames, date_followed, instagram_links
    # Opening the html file
    print("opening file")
    file_path = os.path.join(settings.BASE_DIR, 'upload/followers_1.html')
    HTMLFile = open(file_path, "r")
    print('file opened')
    # Reading the file
    index = HTMLFile.read()

    # Creating a BeautifulSoup object and specifying the parser
    soup = BeautifulSoup(index, 'html.parser')

    users = soup.find_all('a')
    instagram_links = []
    usernames = []
    date_followed = []
    # Using the prettify method to modify the code
    for user in users:
        instagram_links.append(user.get('href'))
        usernames.append(user.text)
        date_followed.append(user.find_next('div').text)
        # div_tag = user.find_next('div')
    # print(date_followed)

def create_tables():
    global usernames, date_followed, instagram_links
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE followers(
    username VARCHAR(50) NOT NULL,
    date_followed DATE NOT NULL,
    instagram_link VARCHAR(150) NOT NULL,
    PRIMARY KEY(username, date_followed)
);
        """,)
    conn = None
    try:
        # read the connection parameters
        # params = config()

        #establishing the connection
        conn = psycopg2.connect(
        database="postgres", user='postgres', password='password', host='127.0.0.1', port= '5432'
        )
        #Creating a cursor object using the cursor() method
        cur = conn.cursor()

        # create table one by one
        for command in commands:
            cur.execute(command)
        
        for i in range(len(usernames)):
            cur.execute(f'''INSERT INTO followers(username, date_followed, instagram_link) 
            VALUES ('{usernames[i]}', to_timestamp('{date_followed[i]}', 'Mon DD, YYYY, HH:MI AM'), '{instagram_links[i]}')''')
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def read_table():
    global usernames, date_followed, instagram_links

    conn = None
    try:
        # read the connection parameters
        # params = config()

        #establishing the connection
        conn = psycopg2.connect(
        database="postgres", user='postgres', password='password', host='127.0.0.1', port= '5432'
        )
        #Creating a cursor object using the cursor() method
        cur = conn.cursor()
        
        
        cur.execute(f'''SELECT * from followers;''')
        result = cur.fetchall()
        print(result)
        print(len(result))
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def ask_question(prompt):
    global usernames, date_followed, instagram_links, prediction_table
    openai.api_key = os.getenv('OPENAI_API_KEY')
    gpt_prompt = f'''A PostgreSQL Table followers stores the followers of a person on Instagram,
    the date someone followed them, and the follower's instagram link.
    columns=[username, date_followed, instagram_link]

    If you do not know the answer, say "I don't know."
    
    Create a PostgreSQL query with the correct syntax for - {prompt}'''

    response = openai.Completion.create(
    engine="text-davinci-003",
    prompt=gpt_prompt,
    temperature=0.7,
    max_tokens=256,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
    )

    print(response['choices'][0]['text'])
    print()
    print()
    return response['choices'][0]['text']
    # prediction_table.add_data(gpt_prompt,response['choices'][0]['text'])

def get_answer(query):
    conn = None
    try:
        # read the connection parameters
        # params = config()

        #establishing the connection
        conn = psycopg2.connect(
        database="postgres", user='postgres', password='password', host='127.0.0.1', port= '5432'
        )
        #Creating a cursor object using the cursor() method
        cur = conn.cursor()
        
        
        cur.execute(query)
        result = cur.fetchall()
        
        df = DataFrame(result)
        # df.columns = result.keys()
        print(f'received {len(result)} records')
        for i in range(len(result)):
            for j in range(len(result[i])):
                print(result[i][j], end = "   ")
            print()
        # print(result)
        # print(len(result))
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()