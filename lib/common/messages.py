"""

Common terminal messages used across Empire.

Titles, agent displays, listener displays, etc.

"""

import os, sys, textwrap

# Empire imports
# from helpers import *
# from lib.common.helpers import *
from helpers import *


###############################################################
#
# Messages
#
###############################################################

def title(version):
    """
    Print the tool title, with version.
    """
    os.system('clear')
    print "===================================================================================="
    print " Empire: PowerShell post-exploitation agent | [Version]: " + version
    print '===================================================================================='
    print ' [Web]: https://www.PowerShellEmpire.com/ | [Twitter]: @harmj0y, @sixdub, @enigma0x3'
    print '===================================================================================='
    print """
   _______ .___  ___. .______    __  .______       _______ 
  |   ____||   \/   | |   _  \  |  | |   _  \     |   ____|
  |  |__   |  \  /  | |  |_)  | |  | |  |_)  |    |  |__   
  |   __|  |  |\/|  | |   ___/  |  | |      /     |   __|  
  |  |____ |  |  |  | |  |      |  | |  |\  \----.|  |____ 
  |_______||__|  |__| | _|      |__| | _| `._____||_______|

"""

def wrap_string(data, width=48, indent=32, indentAll=False, followingHeader=None):
    """
    Print a option description message in a nicely 
    wrapped and formatted paragraph.

    followingHeader -> text that also goes on the first line
    """

    data = str(data)

    if len(data) > width:
        lines = textwrap.wrap(textwrap.dedent(data).strip(), width=width)
        
        if indentAll:
            returnString = ' '*indent+lines[0]
            if followingHeader: 
                returnString += " " + followingHeader
        else:
            returnString = lines[0]
            if followingHeader: 
                returnString += " " + followingHeader
        i = 1
        while i < len(lines):
            returnString += "\n"+' '*indent+(lines[i]).strip()
            i += 1
        return returnString
    else:
        return data.strip()


def wrap_columns(col1, col2, width1=24, width2=40, indent=31):
    """
    Takes two strings of text and turns them into nicely formatted column output.

    Used by display_module()
    """
    
    lines1 = textwrap.wrap(textwrap.dedent(col1).strip(), width=width1)
    lines2 = textwrap.wrap(textwrap.dedent(col2).strip(), width=width2)

    result = ''

    limit = max(len(lines1), len(lines2))

    for x in xrange(limit):

        if x < len(lines1):
            if x != 0:
                result +=  ' '*indent
            result += '{line: <0{width}s}'.format(width=width1, line=lines1[x])
        else:
            if x == 0:
                result += ' '*width1
            else:
                result += ' '*(indent + width1)

        if x < len(lines2):
            result +=  '  ' + '{line: <0{width}s}'.format(width=width2, line=lines2[x])

        if x != limit-1:
            result += "\n"

    return result


def display_options(options, color=True):
    """
    Take a dictionary and display it nicely.
    """
    for key in options:
        if color:
            print "\t%s\t%s" % (helpers.color('{0: <16}'.format(key), "green"), wrap_string(options[key]))
        else:
            print "\t%s\t%s" % ('{0: <16}'.format(key), wrap_string(options[key]))

def agent_print (agents):
    """
    Take an agent dictionary and display everything nicely.
    """
    print info("Active agents:")

    data = []
    for agent in agents:
        [ID, sessionID, listener, name, delay, jitter, external_ip, internal_ip, username, high_integrity, process_name, process_id, hostname, os_details, session_key, checkin_time, lastseen_time, parent, children, servers, uris, old_uris, user_agent, headers, functions, kill_date, working_hours, ps_version, lost_limit] = agent
        if str(high_integrity) == "1":
            # add a * to the username if it's high integrity 
            username = "*" + username

        data.append([name, internal_ip, hostname, username, 
                    '/'.join([str(process_name), str(process_id)]), 
                    '/'.join([str(delay), str(jitter)]), lastseen_time])

    headers = ['Name', 'Internal IP', 'Machine Name', 'Username', 'Process', 'Delay', 'Last Seen']
    tableify(data, headers=headers)

def display_agents(agents):

    if len(agents)>0:
        agent_print(agents)
    else:
        print helpers.color("[!] No agents currently registered ")



def display_staleagents(agents):
    """
    Take an agent dictionary and display everything nicely.
    """

    if len(agents)>0:
        agent_print(agents)
    else:
        print helpers.color("[!] No stale agents currently registered ")



def display_agent(agent):
    """
    Display an agent all nice-like.

    Takes in the tuple of the raw agent database results.
    """

    # extract out database fields.
    keys = ["ID", "sessionID", "listener", "name", "delay", "jitter", "external_ip", "internal_ip", "username", "high_integrity", "process_name", "process_id", "hostname", "os_details", "session_key", "checkin_time", "lastseen_time", "parent", "children", "servers", "uris", "old_uris", "user_agent", "headers", "functions", "kill_date", "working_hours", "ps_version", "lost_limit"]

    print helpers.color("\n[*] Agent info:\n")

    # turn the agent into a keyed dictionary
    agentInfo = dict(zip(keys, agent))

    for key in agentInfo:
        if key != "functions":
            print "\t%s\t%s" % (helpers.color('{0: <16}'.format(key), "blue"), wrap_string(agentInfo[key], width=70))
    print ""


def display_listeners(listeners):
    """
    Take a listeners list and display everything nicely.
    """

    if len(listeners) > 0:
        print ""    
        print info("Active listeners:\n")
        
        headers = ['ID', 'Name', 'Host', 'Type', 'Delay', 'KillDate', 'Redirect']

        data = []
        for listener in listeners:

            [ID,name,host,port,cert_path,staging_key,default_delay,default_jitter,default_profile,kill_date,working_hours,listener_type,redirect_target,default_lost_limit] = listener

            if not host.startswith("http"):
                if cert_path and cert_path != "":
                    host = "https://" + host
                else:
                    host = "http://" + host

                host += ":" + str(port)

            data.append([ID, name, host, listener_type, '/'.join([str(default_delay), str(default_jitter)]), kill_date, redirect_target])
        
        tableify(data, headers=headers)
    else:
        print warning("[!] No listeners currently active ")

def display_listener(options):
    """
    Displays a listener's information structure.
    """

    info("Listener Options:")
    headers = ['Name', 'Required', 'Value', 'Description']

    data = []
    for option,values in options.iteritems():
        # if there's a long value length, wrap it
        data.append([option, values.get('Required', 'False'), values.get('Value'), values.get('Description', '')])
        # if len(str(values['Value'])) > 33:
            # print "  %s%s%s" % ('{0: <18}'.format(option), '{0: <12}'.format(("True" if values['Required'] else "False")), '{0: <33}'.format(wrap_string(values['Value'], width=32, indent=32, followingHeader=values['Description'])))
        # else:
            # print "  %s%s%s%s" % ('{0: <18}'.format(option), '{0: <12}'.format(("True" if values['Required'] else "False")), '{0: <33}'.format(values['Value']), values['Description'])

    tableify(data, headers=headers)


def display_listener_database(listener):
    """
    Displays a listener's information from the database.

    Transforms the tuple set to an options dictionary and calls display_listener().
    """

    [ID,name,host,port,certPath,stagingKey,defaultDelay,defaultJitter,defaultProfile,killDate,workingHours,listenerType,redirectTarget, defaultLostLimit] = listener

    options = {
        'ID' : {
            'Description'   :   'Listener ID.',
            'Required'      :   True,
            'Value'         :   ''
        },
        'Name' : {
            'Description'   :   'Listener name.',
            'Required'      :   True,
            'Value'         :   ''
        },
        'Host' : {
            'Description'   :   'Hostname/IP for staging.',
            'Required'      :   True,
            'Value'         :   ''
        },
        'Type' : {
            'Description'   :   'Listener type (native, pivot, hop).',
            'Required'      :   True,
            'Value'         :   ''
        },
        'RedirectTarget' : {
            'Description'   :   'Listener target to redirect to for pivot/hop.',
            'Required'      :   False,
            'Value'         :   ''
        },
        'StagingKey' : {
            'Description'   :   'Staging key for initial agent negotiation.',
            'Required'      :   True,
            'Value'         :   ''
        },
        'DefaultDelay' : {
            'Description'   :   'Agent delay/reach back interval (in seconds).',
            'Required'      :   True,
            'Value'         :   ''
        },
        'DefaultJitter' : {
            'Description'   :   'Jitter in agent reachback interval (0.0-1.0).',
            'Required'      :   True,
            'Value'         :   ''
        },
        'DefaultLostLimit' : {
            'Description'   :   'Number of missed checkins before exiting',
            'Required'      :   True,
            'Value'         :   ''
        },
        'DefaultProfile' : {
            'Description'   :   'Default communication profile for the agent.',
            'Required'      :   True,
            'Value'         :   ''
        },
        'CertPath' : {
            'Description'   :   'Certificate path for https listeners.',
            'Required'      :   False,
            'Value'         :   ''
        },
        'Port' : {
            'Description'   :   'Port for the listener.',
            'Required'      :   True,
            'Value'         :   ''
        },
        'KillDate' : {
            'Description'   :   'Date for the listener to exit (MM/dd/yyyy).',
            'Required'      :   False,
            'Value'         :   ''
        },
        'WorkingHours' : {
            'Description'   :   'Hours for the agent to operate (09:00-17:00).',
            'Required'      :   False,
            'Value'         :   ''
        }
    }

    options['ID']['Value'] = ID
    options['Name']['Value'] = name
    options['Host']['Value'] = host
    options['Port']['Value'] = port
    options['CertPath']['Value'] = certPath
    options['StagingKey']['Value'] = stagingKey
    options['DefaultDelay']['Value'] = defaultDelay
    options['DefaultJitter']['Value'] = defaultJitter
    options['DefaultProfile']['Value'] = defaultProfile
    options['KillDate']['Value'] = killDate
    options['WorkingHours']['Value'] = workingHours
    options['Type']['Value'] = listenerType
    options['RedirectTarget']['Value'] = redirectTarget
    options['DefaultLostLimit']['Value'] = defaultLostLimit

    display_listener(options)


def display_stager(stagerName, stager):
    """
    Displays a stager's information structure.
    """
    
    print "Name: {}".format(stager.info['Name'])
    print "Description:"
    desc = wrap_string(stager.info['Description'], width=50, indent=2, indentAll=True)
    if len(desc.splitlines()) == 1:
        print "  " + str(desc)
    else:
        print desc

    # print out any options, if present
    if stager.options:
        # print color("Options:", color='blue')
        print ""
        data = []
        headers = ['Name', 'Required', 'Value', 'Description']

        for option,values in stager.options.iteritems():
            data.append([option, values.get('Required', 'False'), values.get('Value', ''), values.get('Description', '')])

        tableify(data, headers=headers)


def display_module(moduleName, module):
    """
    Displays a module's information structure.
    """
    
    print '\n{0: >17}'.format("Name: ") + str(module.info['Name'])
    print '{0: >17}'.format("Module: ") + str(moduleName)
    print '{0: >17}'.format("NeedsAdmin: ") + ("True" if module.info['NeedsAdmin'] else "False")
    print '{0: >17}'.format("OpsecSafe: ") + ("True" if module.info['OpsecSafe'] else "False")
    print '{0: >17}'.format("MinPSVersion: ") + str(module.info['MinPSVersion'])
    print '{0: >17}'.format("Background: ") + ("True" if module.info['Background'] else "False")
    print '{0: >17}'.format("OutputExtension: ") + (str(module.info['OutputExtension']) if module.info['OutputExtension'] else "None")

    print "\nAuthors:"
    for author in module.info['Author']:
        print "  " +author

    print "\nDescription:"
    desc = wrap_string(module.info['Description'], width=60, indent=2, indentAll=True)
    if len(desc.splitlines()) == 1:
        print "  " + str(desc)
    else:
        print desc

    # print out any options, if present
    if module.options:
        print "\nOptions:\n"
        headers = ['Name', 'Required', 'Value', 'Description']
        data = []

        for option,values in module.options.iteritems():
            data.append([str(option), values.get('Required', 'False'), str(values.get('Value', '')), str(values.get('Description', ''))])

        tableify(data, headers=headers)


def display_module_search(moduleName, module):
    """
    Displays the name/description of a module for search results.
    """

    print " " + helpers.color(moduleName, "blue") + "\n"
    # width=40, indent=32, indentAll=False,
    
    lines = textwrap.wrap(textwrap.dedent(module.info['Description']).strip(), width=70)
    for line in lines:
        print "\t" + line

    print "\n"

def display_credentials(creds):
    # print color("Options:", 'blue')
    print ""
    headers = ['CredID', 'CredType', 'Domain', 'Username', 'Password', 'Host', 'Notes', 'SID']
    tableify(creds, headers=headers)
