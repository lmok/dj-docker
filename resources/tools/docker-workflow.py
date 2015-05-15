from build import build
from push import push
from shell import shell
from auth import Authenticator
from datetime import datetime
import sys
import argparse
import os

def run():
    try:

        # Read CL arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('repository', help='Repository of the built image, e.g. timmy/testy_image')
        parser.add_argument('-p', '--port', help='Port in docker configuration for the daemon. Defaulted to :4243.', 
            type=int, default=4243)
        parser.add_argument('-w', '--workspace', help='Location of project with Dockerfile at its root. Defaulted to $WORKSPACE.', 
            default=os.getenv('WORKSPACE'))
        parser.add_argument('-t', '--tag', help='Tag for the image. Defaulted to y-m-d-h-m-s (now).', 
            default=datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
        parser.add_argument('-cp', '--config_path', help='Path to the docker config file. Default is /home/jenkins/.dockercfg', 
            default='/home/jenkins/.dockercfg')


        # Look up gateway IP for docker daemon
        code, lines = shell("netstat -nr | grep '^0\.0\.0\.0' | awk '{print $2}'")
        assert code == 0, 'failure to lookup our gateway IP ?'
        host = lines[0]
        #assert host != '', 'Could not find gateway IP'

        args = parser.parse_args()
        repo = args.repository
        print "Repository set to {0}".format(repo)

        port = args.port
        host = "{0}:{1}".format(host, port)
        print "Daemon host set to {0}".format(host)

        workspace = args.workspace
        assert os.getenv('WORKSPACE') != '', 'No $WORKSPACE environment variable. Are you calling this from the Jenkins master?'
        print "Workspace set to {0}".format(workspace)

        tag = args.tag
        print "Tag set to {0}".format(tag)

        config_path = args.config_path
        print "Path to docker config set to {0}".format(config_path)

        authenticator = Authenticator()

        # Enter workflow below
        build(workspace, host, repo, tag, authenticator=authenticator)
        push(host, repo, tag, authenticator=authenticator)

        return 0

    except Exception as e:

        print e
        return 1

run()