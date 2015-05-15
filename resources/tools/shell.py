from subprocess import Popen, PIPE

def shell(snippet):
    """
    Helper invoking a shell command and returning its stdout broken down by lines as a list. The sub-process
    exit code is also returned.
    :type snippet: str
    :param snippet: shell snippet, e.g "echo foo > /bar"
    :rtype: (int, list) 2-uple
    """
    print "Entering shell to run: ${0}".format(snippet)
    pid = Popen(snippet, shell=True, stdout=PIPE, stderr=PIPE)
    pid.wait()
    code = pid.returncode
    out = pid.stdout.read().split('\n')
    return code, out