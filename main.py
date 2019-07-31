import sys
import logging
import getpass
import sleekxmpp
from optparse import OptionParser
from sleekxmpp.exceptions import IqError, IqTimeout


class Register(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        #Evento de registro
        self.add_event_handler("register", self.register)
        #Evento de start
        self.add_event_handler("session_start", self.start)

        #Procesa el evento session_start
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
            logging.info("Se creo la cuenta: %s!" % self.boundjid)
        except IqError as e:
            logging.error("No se pudo registrar la cuenta %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("No hubo respuesta del servidor")
            self.disconnect()


class EchoBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):

        sleekxmpp.ClientXMPP.__init__(self, jid, password)


        #Evento de start
        self.add_event_handler("session_start", self.start)
        #Evento de envio de mensaje
       
        self.add_event_handler("message", self.message)
        


    #Procesa el evento session_start
    def start(self, event):
        print('Session start')
        self.send_presence()
        self.get_roster()


    #Procesa los mensajes entrantes 
    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Se envio\n%(body)s" % msg).send()
            print(msg['body'])



    def send_message(self, recipient, msg):
        self.recipient = recipient
        self.msg = msg
        self.send_message(mto=self.recipient,
                          mbody=self.msg,
                          mtype='chat')
    def group_message():
        pass

    #Nos imprime todos los usuarios
    def get_users(self):
        print(self.get_roster())

    def exit(self):
        self.disconnect()
    
class SendMsgBot(sleekxmpp.ClientXMPP):

    """
    A basic SleekXMPP bot that will log in, send a message,
    and then log out.
    """

    def __init__(self, jid, password, recipient, message):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # The message we wish to send, and the JID that
        # will receive it.
        self.recipient = recipient
        self.msg = message

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        self.get_roster()

        self.send_message(mto=self.recipient,
                          mbody=self.msg,
                          mtype='chat')

        # Using wait=True ensures that the send queue will be
        # emptied before ending the session.
        self.disconnect(wait=True)

if __name__ == '__main__':

    print('1. Login')
    print('2. Register')
    x = input('Ingrese el número de la opción que desea: \n') 

    optp = OptionParser()

    #Opciones de output
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)
    #Opciones de JID y password .
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    #Mensaje y a quien
    optp.add_option("-t", "--to", dest="to",
                    help="JID to send the message to")
    optp.add_option("-m", "--message", dest="message",
                    help="message to send")

    opts, args = optp.parse_args()

    #Setear el login
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = input("Username: " )
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")

    if(x =='1'):
        #Setup de mi clase EchoBot
        print("Se esta iniciando sesion")
        xmpp = EchoBot(opts.jid, opts.password)
    
    elif(x=='2'):
        print("Se esta registrando")
        xmpp = Register(opts.jid, opts.password)


    if opts.to is None:
        opts.to = input("Send To: ")
    if opts.message is None:
        opts.message = input("Message: ")
    xmpp = SendMsgBot(opts.jid, opts.password, opts.to, opts.message)

    

        
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0199') # XMPP Ping
    xmpp.register_plugin('xep_0004') # Data forms
    xmpp.register_plugin('xep_0066') # Out-of-band Data
    xmpp.register_plugin('xep_0077') # In-band Registration
        

    xmpp['xep_0077'].force_registration = True

 
    

    #Conexion con el server
    if xmpp.connect():
        
        xmpp.process(block=True)
        print("Done")
       
    else:
        print("Unable to connect.")

