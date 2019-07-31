import sys
import logging
import getpass
import sleekxmpp
from optparse import OptionParser
from sleekxmpp.exceptions import IqError, IqTimeout
import ssl

class Chat(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        #Event Handlers 
        #register
        self.add_event_handler("register", self.register)
        #start
        self.add_event_handler("session_start", self.start)
        #message
        self.add_event_handler("message", self.message, threaded=True)

    def start(self, event):
        print('Session start')
        self.send_presence()
        self.get_roster()
            
    def register(self, iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            resp.send(now=True)
            logging.info("Account Created: %s!" % self.boundjid)
        except IqError as e:
            logging.error("Unable to register: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("No response from the server")
            self.disconnect()

    def remove_user(self):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['from'] = self.boundjid.user
        resp['register'] = ' '
        resp['register']['remove'] = ' '
        try:
            print(resp)
            resp.send(now=True)
            print("Account deleted: %s" % self.boundjid)
        except IqError as e:
            logging.error("Unable to delete account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("No response from the server")
            self.disconnect()
    
    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print(str(msg['from']) + ": " + msg['body'])


if __name__ == '__main__':

    optp = OptionParser()

    #Debugging stuff
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    #User Stuff
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-t", "--to", dest="to",
                    help="JID to send the message to")
    optp.add_option("-m", "--message", dest="message",
                    help="message to send")

    opts, args = optp.parse_args()

    #logging config
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    print('Type 1 to Login')
    print('Type 2 to Register')
    x = input(': ') 

    if opts.jid is None:
        opts.jid = input("Username: " )
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")

    xmpp = Chat(opts.jid, opts.password)

    if(x=='1'):
        xmpp.del_event_handler("register", xmpp.register)

    #plugins
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0199') # XMPP Ping
    xmpp.register_plugin('xep_0004') # Data forms
    xmpp.register_plugin('xep_0066') # Out-of-band Data
    xmpp.register_plugin('xep_0077') # In-band Registration
    xmpp.register_plugin('xep_0060') # PubSub
 
    xmpp['feature_mechanisms'].unencrypted_plain = True
    xmpp.ssl_version = ssl.PROTOCOL_TLS

    #Conexion con el server
    if xmpp.connect(('alumchat.xyz', 5222)):
        
        xmpp.process(block=False)
        while True:
            print('Press:')
            print('1 to disconnect')
            print('2 to delete account from server')
            print('3 to list users')
            print('4 to send a message')
            print('5 to add friend')
            y = input(": ")

            #disconnect
            if(y == '1'):
                print('goodbye')
                xmpp.disconnect()
                break
            
            #delete account
            elif(y == '2'):
                xmpp.remove_user()
                xmpp.disconnect()
                break
            
            #list users
            elif(y == '3'):
                print('List of Users:')
                print(xmpp.client_roster.keys())
                print(' ')
            
            #send message
            elif(y == '4'):
                usr = input('Who do you want to send a message?')
                mssg = input('What message do you want to send?')
                print('Sending...')
                xmpp.send_message(mto=usr, mbody=mssg, mtype='chat')
            
            #add friend
            elif(y == '5'):
                friend = input('Who do you want to be friends with?')
                xmpp.send_presence(pto=friend, ptype='subscribe')

       
    else:
        print("Unable to connect.")

