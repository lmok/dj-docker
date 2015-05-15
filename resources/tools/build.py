from subprocess import Popen, PIPE
from datetime import datetime
from shell import shell
import sys
import os 
import shutil
import re
import json

def build(workspace, host, repository, tag, authenticator=None):
    
    try:
        # Check that Dockerfile is in cwd 
        assert os.path.isfile('Dockerfile'), 'Dockerfile is missing in cwd.'

        # Tar job
        tar_out = "{0}.tgz".format(os.path.basename(workspace if workspace[-1] != "/" else workspace[:-1]))
        command = """tar cfz {0} -C {1} .""".format(tar_out, workspace)
        code, lines = shell(command)
        #assert code == 0, 'tar failure'

        # Upload build job
        command = """curl --header "Content-Type:application/octet-stream" --data-binary @{0} http://{1}/build?forcerm=1\&t={2}:{3}""".format(
            tar_out, host, repository, tag)
        code, lines = shell(command)
        assert code == 0, 'non zero ({0}) build curl exit code ?'.format(code)
        assert len(lines) > 1, 'no stdout (docker daemon error ?)'

        # # - retrieve the build id using a regex (super ugly)
        # try:
        #     last = json.loads(lines[-2])

        # except ValueError:

        #     assert 0, 'invalid dockerfile ("%s")' % lines[-2]

        # assert 'stream' in last, 'build error ("%s")' % last
        # matched = re.match('Successfully built ([a-zA-Z0-9]+)\n', last['stream'])
        # assert matched, 'unable to find the image id ("%s")' % last['stream']
        # aka = matched.group(1)

        # # - fix the damn build image name bug thing and finally tag our image as 'latest'
        # command = """curl -X POST http://{0}/images/{1}/tag?repo={2}\&force=1\&tag={3}""".format(host, aka, repository, tag)
        # print command
        # code, lines = shell(command)

        os.remove(tar_out)

    except Exception as e:
        print "Build Exception"
        print e
        raise e