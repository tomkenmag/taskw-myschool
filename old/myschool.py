#!/usr/bin/env python3
"""
[ T-308-PRLA ] Verkefni 5

Script to upload a file and/or message to MySchool by passing file and/or 
message and optionally the direct URL to the assignment.

Tómas Ken Magnússon
tomasm12@ru.is
"""
from bs4 import BeautifulSoup
from getpass import getpass
from requests.auth import HTTPBasicAuth
import argparse
import bs4
import os
import re
import requests


def get_choice( unfinished_table, head, status):
    """
    Formats the list of unfinished assignments and prompts the user for an 
    assignment.

    Parameters
    ----------
    unfinished_table : list of tuples of list of string and string
    The list of the assignments, where every assignment is a list of strings,
    which course and so and and the URL of the assignment.

    head : list of strings
    The header of the table.

    Return 
    ------
    Integer which is the index of the assignment the user choses.
    """
    rows, columns = os.popen('stty size', 'r').read().split()
    width = int(columns) // 5
    print("Næstu verkefni: ")
    print("-"*int(columns))
    print('\033[1m','#'.ljust(3),
        head[0].ljust(width),head[1].ljust(int(width*1.5)),
        head[2].ljust(int(width*0.7)),head[4].ljust(width),'\033[0m')
    num = 0
    for i,j in unfinished_table:
        num += 1
        print(('('+str(num)+')').ljust(4),
            i[0].ljust(width), i[1].ljust(int(width*1.5)),
            i[2].ljust(int(width*0.7)), i[4].ljust(width))
    print("-"*int(columns))
    while not status:
        strInput = input('Which assignment: ')
        try:
            numAssignment = int(strInput)
        except ValueError:
            print("Invalid choice.\n")
        else:
            if 0 < numAssignment <= len(unfinished_table):
                return numAssignment
            else:
                print("Invalid choice.\n")

def get_download_url( html ):
    """
    Finds the url for downloading the assignment files by parsing the html of
    the assignment page.

    @TODO
    Implement to parse the html to find the download urls.

    Parameters
    ----------
    html : str
    The html of the assignment file. 
    """
    return None

def get_auth():
    """
    Gets the username and password from the user for MySchool.

    Return
    ------
    Tuple of two strings, the username and password. 
    """
    username = input("Username: ")
    password = getpass()
    return (username,password)

def get_auth_from_file( path ):
    """
    Extracts MySchool authentication from a plain text file(I know).

    Parameters
    ----------
    dir : str
    Path of the text file containing the username and passwords.

    Return
    ------
    Tuple of strings, the username and the password.
    """
    with open( path ) as f:
        return re.split('\s+', f.read() )


def get_assignment_list( html ):
    """
    Takes an html as string, parses it and returns a table of unfinished 
    assignments.

    Parameters
    ----------
    html : str
    The html as string

    Return
    ------
    Returns a tuple of head of the table and the table itself.
    The head is a list of string and table is a list of list of strings.
    """
    soup = BeautifulSoup(html,'html.parser')
    tables = soup.find_all('tbody')
    unfinished_assignments = tables[0].find_all('tr')
    unfinished_table = [ [ col.get_text() for col in row if 
            type(col)==bs4.element.Tag] for row in unfinished_assignments]
    head = unfinished_table[0]
    links = [ i['href'] for i in tables[0].find_all('a')]
    unfinished_table = list(zip(unfinished_table[1:],links))
    return head, unfinished_table

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('files'	,nargs='*', type=str,
            help="Files to be uploaded.")
    parser.add_argument('-u','--url',type=str, dest='url',
            help='URL of an assignment.')
    parser.add_argument('-m','--message', type=str, dest='message',
            help='Message to be sent with the file.')
    parser.add_argument('-s','--status', dest='status',action='store_true',
            help='Print the status of current assignments.')
    parser.add_argument('-g', '--get', dest='get', action='store_true',
            help='Download the assignment files to current directory.')
    parser.add_argument('dir', type=str, nargs='?',default=os.getcwd(),
            help='Download directory of the assignment files.')
    args = parser.parse_args()
    if args.status and (args.files or args.message or args.url or args.get):
        print('Error: Status flag must be passed alone.')
        parser.print_help()
        exit()
    if not (args.files or args.message or args.status):
        print('Error: Either message or file has to be specified.')
        parser.print_help()
        exit()
    return args


if __name__=="__main__":
    args = parse_args()

    MYSCHOOL = 'https://myschool.ru.is/myschool/'
    #Authentication
    try:
        sess = requests.Session()
    except:
        print("Connection error, check internet connection.")
        exit()

    sess.auth = get_auth()
    #sess.auth = tuple(get_auth_from_file('/home/shimo/Documents/myschool_auth'))

    request = sess.get('https://myschool.ru.is/myschool/?Page=Exe&ID=1.12')
    if request.ok:
        head, unfinished_table = get_assignment_list( request.text )
        # If user passed the url to the script the list will not be printed.
        if not args.url:
            choice = get_choice(unfinished_table, head, args.status)
            if args.status:
                exit()
            assignmentUrl = MYSCHOOL + unfinished_table[choice-1][1]
        else:
            assignmentUrl = args.url

        verkefniRequest = sess.get(assignmentUrl)
        if not verkefniRequest.ok:
            print('Error: Invalid url.\n')
            parser.print_help()
            exit()
        verkefniSoup = bs4.BeautifulSoup(verkefniRequest.text,'html.parser')

        # Determine the message to be sent, unchanged or new.
        if args.message:
            postMessage = args.message
        else:
            postMessage = verkefniSoup.find('textarea').get_text()

        postUrl = MYSCHOOL + verkefniSoup.find('form', id='form1')['action']

        # If user added files they will be processed, else only the message will.
        if args.files:
            for file in args.files:
                try:
                    files = { 'FILE' : (os.path.basename(file),open(file, 'rb'))}
                except IOError as e:
                    print(e)
                else:
                    data = { 'athugasemdnemanda' : postMessage }
                    postResponse = sess.post(postUrl, files=files, data=data)
                    if postResponse.ok:
                        print(file, " uploaded to assignment.")
                    else:
                        print("Error when uploading files.")
        else:
            files = { 'FILE' : ('','')}
            data = { 'athugasemdnemanda' : postMessage }
            postResponse = sess.post(postUrl, files=files, data=data)
            if postResponse.ok:
                print('Message posted to assignment.\n')

    elif request.status_code == 401:
        print("Error: Wrong password or username.\n")
    else:
        print("Error: Check your connection.")
