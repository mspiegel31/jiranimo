import jira
import getpass

sprint_name_re = re.compile('name=(.+?),')

def get_jira_context(options, auth_tup):
    return jira.JIRA(options, basic_auth=auth_tup)

def get_credentials():
    pass
