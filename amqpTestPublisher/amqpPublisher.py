import pika
import time
import os.path
import sys
import getopt


def sendMessages(message, config, options):
    messageCount = options['messageCount']
    delay = options['delay']

    # connection settings
    credentials = pika.PlainCredentials(config['user'], config['password'])
    connectionParams = pika.ConnectionParameters(
        host=config['host'], port=int(config['port']), credentials=credentials)

    print('connecting to message broker')
    connection = pika.BlockingConnection(connectionParams)
    print('connecting to exchange')
    channel = connection.channel()
    channel.exchange_declare(
        exchange=config['exchange'], exchange_type=config['exchange_type'], durable=bool(config['durable']))
    print('connection established')

    print('start sending messages')
    for i in range(0, messageCount):
        channel.basic_publish(exchange='wacodis.dataenvelope.creation',
                              routing_key='',
                              body=message)
        print('message (%i) sent with body:\n%s' % ((i+1), message))

        if i != (messageCount-1):
            print('wait for %d seconds' % delay)
            time.sleep(delay)

    print('finished sending messages')

    connection.close()


def readMessage(filename='message.txt'):
    message = 'default message'

    if not os.path.isfile(filename):
        print('file (Message) does not exist (%s)' % filename)
    else:
        with open(filename) as f:
            print('reading message from file (%s)' % filename)
            message = f.read()

    print('message:\n%s' % message)
    return message


def readConfiguration(filename='configuration.txt'):
    config = {'host': 'localhost', 'port': '5672', 'user': 'guest', 'password': 'guest',  # default broker config
              'exchange': 'default', 'exchange_type': 'topic', 'durable': 'True'}  # default exchange config

    if not os.path.isfile(filename):
        print('file (Configuration) does not exist (%s)' % filename)
    else:
        with open(filename, 'r') as f:
            print('reading configuration from file (%s)' % filename)
            for line in f:
                spline = line.split('=', 1)
                config[spline[0]] = spline[1].strip()

    print('configuration:\n%s' % str(config))
    return config

# parse command line arguments and override global variables


def readCommandLineArgs():
    optionsDict = {'messageFile': 'message.txt',
                   'configFile': 'configuration.txt', 'delay': 1, 'messageCount': 1}
    options, args = getopt.getopt(sys.argv[1:], 'm:c:d:t:')

    print('parsing command line arguments')

    for option, arg in options:
        if option == '-m':  # path to message file
            optionsDict['messageFile'] = arg
        elif option == '-c':  # path to configuration file
            optionsDict['configFile'] = arg
        elif option == '-d':  # delay between messages
            optionsDict['delay'] = int(arg)
        elif option == '-t':  # number of messages to send
            optionsDict['messageCount'] = int(arg)

    print('options:\n%s' % str(options))
    return optionsDict


if __name__ == "__main__":
    # parse command line arguments and override global variables
    options = readCommandLineArgs()
    message = readMessage(options['messageFile'])  # parse message to send
    # parse broker configuration
    config = readConfiguration(options['configFile'])

    # connect to broker and send messages
    sendMessages(message, config, options)
