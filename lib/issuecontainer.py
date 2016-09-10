from collections import namedtuple
BaseIssueContainer = namedtuple('IssueContainer', [
                            'raw',
                            'key',
                            'url',
                            'assignee',
                            'summary',
                            'status',
                            'resolution_date',
                            'original_estimate',
                            'time_spent',
                            'total_time_spent',
                            'story_points'])

class IssueContainer(BaseIssueContainer):
    """provides intialization for BaseIssueContainer"""
    __slots__ = ()


    def __new__(cls, issue):
        fields = issue['fields']
        dictionary = {
            'raw': issue,
            'key': issue.get('key'),
            'url': issue.get('self'),
            'assignee': fields.get('assignee').get('displayName') if fields.get('assignee') else None,
            'summary': fields.get('summary'),
            'status': fields.get('status').get('name') if fields.get('status') else None,
            'resolution_date': fields.get('resolution_date'),
            'original_estimate': fields.get('timeestimate'),
            'time_spent': fields.get('timespent'),
            'total_time_spent': fields.get('aggregatetimespent'),
            'story_points': fields.get('customfield_10143')
        }
        return super(IssueContainer, cls).__new__(cls, **dictionary)
