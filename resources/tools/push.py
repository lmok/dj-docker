from shell import shell

def push(host, repository, tag=None, stream=False, insecure_registry=False, authenticator=None):
    try:

        # Get the header for the post 
        header = authenticator.auth_token(host, repository, tag, stream, insecure_registry)
        tag_opt = '?tag={0}'.format(tag)
        command = """curl -X POST -H "X-Registry-Auth:{0}" http://{1}/images/{2}/push{3}""".format(header, host, repository, tag_opt)
        code, lines = shell(command)
        assert code == 0, 'non zero ({0}) push curl exit code ?'.format(code)

    except Exception as e:

        print "Push Exception"
        print e
        raise e