from collections import OrderedDict, namedtuple

field_mappings = OrderedDict([
    ('assignee', 'assignee'),
    ('summary', 'summary'),
    ('status', 'status'),
    ('resolution_date', 'resolution_date'),
    ('original_estimate', 'aggregatetimeoriginalestimate'),
    ('time_spent', 'timespent'),
    ('total_time_spent', 'aggregatetimespent'),
    ('story_points', 'customfield_10143'),
    ('work_ratio', 'workratio'),
    ('num_subtasks', 'subtasks'),
])


def format_time(number):
    if number:
        return number / 60**2


class IssueContainer(namedtuple('BaseIssueContainer', ['raw', 'key', 'url'] + list(field_mappings.keys()))):
    """Lightweight processing for Jira data"""
    __slots__ = ()
    field_mappings = field_mappings

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
            'original_estimate': format_time(fields.get('aggregatetimeoriginalestimate')),
            'time_spent': format_time(fields.get('timespent')),
            'total_time_spent': format_time(fields.get('aggregatetimespent')),
            'story_points': fields.get('customfield_10143'),
            'work_ratio': fields.get('workratio'),
            'num_subtasks': len(fields.get('subtasks')) if fields.get('subtasks') else 0,

        }
        return super(IssueContainer, cls).__new__(cls, **dictionary)
