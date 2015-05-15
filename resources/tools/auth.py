import json
import base64
import fileinput
import getpass
import six
import os

class Authenticator:

    def __init__(self, index_url=None, docker_config_path=None, docker_config_name=None):
        # A significant part of this comes from docker-py. 
        self.INDEX_URL = 'https://index.docker.io/v1/' if index_url is None else index_url
        self.DOCKER_CONFIG_FILENAME = '.dockercfg' if docker_config_name is None else docker_config_name
        self.DOCKER_CONFIG_PATH = None


    def expand_registry_url(hostname, insecure=False):
        if hostname.startswith('http:') or hostname.startswith('https:'):
            return hostname
        if utils.ping_registry('https://' + hostname):
            return 'https://' + hostname
        elif insecure:
            return 'http://' + hostname
        else:
            raise Exception(
                "HTTPS endpoint unresponsive and insecure mode isn't enabled."
            )


    def convert_to_hostname(self, url):
        return url.replace('http://', '').replace('https://', '').split('/', 1)[0]


    def encode_header(self, auth):
        auth_json = json.dumps(auth).encode('ascii')
        return base64.b64encode(auth_json)


    def decode_auth(self, auth):
        if isinstance(auth, six.string_types):
            auth = auth.encode('ascii')
        s = base64.b64decode(auth)
        login, pwd = s.split(b':', 1)
        return login.decode('ascii'), pwd.decode('ascii')


    def resolve_repository_name(self, repo_name, insecure=False):
        if '://' in repo_name:
            raise Exception(
                'Repository name cannot contain a scheme ({0})'.format(repo_name))
        parts = repo_name.split('/', 1)
        if '.' not in parts[0] and ':' not in parts[0] and parts[0] != 'localhost':
            # This is a docker index repo (ex: foo/bar or ubuntu)
            return self.INDEX_URL, repo_name
        if len(parts) < 2:
            raise Exception(
                'Invalid repository name ({0})'.format(repo_name))

        if 'index.docker.io' in parts[0]:
            raise Exception(
                'Invalid repository name, try "{0}" instead'.format(parts[1])
            )

        return self.expand_registry_url(parts[0], insecure), parts[1]


    def resolve_authconfig(self, authconfig, registry=None):
        """
        Returns the authentication data from the given auth configuration for a
        specific registry. As with the Docker client, legacy entries in the config
        with full URLs are stripped down to hostnames before checking for a match.
        Returns None if no match was found.
        """
        # Default to the public index server
        registry = self.convert_to_hostname(registry) if registry else self.INDEX_URL

        if registry in authconfig:
            return self.authconfig[registry]

        for key, config in six.iteritems(authconfig):
            if self.convert_to_hostname(key) == registry:
                return config

        return None


    def load_config(self):
        """
        Loads authentication data from a Docker configuration file in the given
        root directory or if config_path is passed use given path.
        """
        conf = {}
        data = None

        config_file = self.DOCKER_CONFIG_PATH or os.path.join(os.environ.get('HOME', '.'), self.DOCKER_CONFIG_FILENAME)

        # if config path doesn't exist return empty config
        if not os.path.exists(config_file):
            conf["username"] = raw_input("username: ")
            conf["password"] = getpass.getpass("password: ")
            conf["email"] = raw_input("email: ")
            addr = raw_input("serveraddress: ")
            conf["serveraddress"] = self.INDEX_URL if addr == '' else addr
            conf["auth"] = ""
            return {conf["serveraddress"]: conf}

        # First try as JSON
        try:
            with open(config_file) as f:
                conf = {}
                for registry, entry in six.iteritems(json.load(f)):
                    username, password = self.decode_auth(entry['auth'])
                    conf[registry] = {
                        'username': username,
                        'password': password,
                        'email': entry['email'],
                        'serveraddress': registry,
                    }
                return conf
        except:
            print "Failed to parse docker config file to JSON."

        # If that fails, we assume the configuration file contains a single
        # authentication token for the public registry in the following format:
        #
        # auth = AUTH_TOKEN
        # email = email@domain.com
        try:
            data = []
            for line in fileinput.input(config_file):
                data.append(line.strip().split(' = ')[1])
            if len(data) < 2:
                # Not enough data
                raise Exception(
                    'Invalid or empty configuration file!')

            username, password = self.decode_auth(data[0])
            conf[self.INDEX_URL] = {
                'username': username,
                'password': password,
                'email': data[1],
                'serveraddress': self.INDEX_URL,
            }
            return conf
        except:
            "Failed to parse docker config file manually."
            
        # If all fails, return an empty config
        return {}


    def auth_token(self, host, repository, tag=None, stream=False, insecure_registry=False):
        
        registry, repo_name = self.resolve_repository_name(
                repository, insecure=insecure_registry
            )
        u = "{0}/images/{1}/push".format(host, repository)
        params = {
            'tag': tag
        }
        headers = {}

        # If we don't have any auth data so far, try reloading the config
        # file one more time in case anything showed up in there.
        auth_configs = self.load_config()
        authcfg = self.resolve_authconfig(auth_configs, registry)

        # Do not fail here if no authentication exists for this specific
        # registry as we can have a readonly pull. Just put the header if
        # we can.
        header = self.encode_header(authcfg)

        return header
