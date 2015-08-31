import httplib2
import os
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from apiclient import errors
import json
import csv
from numpy import genfromtxt ,recfromcsv
import itertools

f = open('Email.csv', 'ab')
writer = csv.writer(f)
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'Cs.json'
APPLICATION_NAME = 'Track Emails'


def get_credentials(): #login if not already logged in. 
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print 'Storing credentials to ' + credential_path
    return credentials


credentials = get_credentials()  
http = credentials.authorize(httplib2.Http())
service = discovery.build('gmail', 'v1', http=http)

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

def ListMessagesMatchingQuery(user_id, query=''):
  
  try:
    response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])
    
    getAddress(messages)
    print ("Query Done...")   
    return messages
  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def getAddress(array_of_response):   
    try:
        print ("Getting Ids...")
        for email in array_of_response:
           email_id = email.values()[0] #getting all the ids of email
           getFromAddress(email_id)     #getting the from address of perticular id
           print ("...")
    except Exception, err:
        print "erorr" ,err

def getFromAddress(id):
    message = service.users().messages().get(userId='me', id=id, format='metadata').execute() #metadata used for small responses size
    if message:
        if 'payload' in message:
            payload = message['payload']
            if 'headers' in payload:
                headers = payload['headers']
                for name in headers:
                    if 'name' in name:
                        fromEmail = name['name']
                        if fromEmail == 'From':
                            """print name['value']
                            print name.values()"""
                            for key in name.values():
                                # print key
                                if key != "From":                                  
                                    writer.writerow(["From", key])   #csv writer , creating a array of addresses         
                           
           
def filterResult():
    print " \nFiltering Data..."
    my_data = recfromcsv('Email.csv', delimiter=',') #converting CSV to tuple to use "set" function
    uniq = set(itertools.chain.from_iterable(my_data))
    print "Filtering Done..."
    if len(uniq) > 0:
        for u in uniq:
            print u.split('@').pop().split('>')[0]
    else:
        print "No track found for your Email"
    
        
def main():
    print "Querying..."        
    ListMessagesMatchingQuery('me', 'from:no-reply') #main query to serach api GoogleEmailAPI
#   you can chain above methods to broaden your search results. 
    f.close()    
    filterResult()
    
if __name__ == '__main__':
    main()
    

  