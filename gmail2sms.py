from __future__ import print_function
import httplib2
import os
from twilio.rest import Client
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import json

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def send_sms(mes):
    with open('twilio_credentials.json') as file:
        data=json.load(file)
    account_sid=data["account_sid"]
    auth_token=data["auth_token"]
    client=Client(account_sid,auth_token)
    send=client.api.account.messages.create(to=data["to"],from_=data["from"],body=mes)


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_message(message):
        return str(message['snippet']).encode('ascii','ignore')

def get_sender(message):
    for i in range(len(message['payload']['headers'])):
        if(str(message['payload']['headers'][i]['name'])=='From'):
            return(str(message['payload']['headers'][i]['value']).encode('ascii','ignore'))

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().messages().list(userId='me',maxResults=1).execute()
    message_id=results['messages'][0]['id']
    message = service.users().messages().get(userId='me',id=message_id).execute()
    snippet=get_message(message)
    sender=get_sender(message)

    print ("You have a new mail from "+sender)
    print (snippet)
    send_sms("You have a new mail from "+sender+": "+snippet)


if __name__ == '__main__':
    main()
