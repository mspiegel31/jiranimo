import pytest
from jiranimo.issuecontainer import IssueContainer

@pytest.fixture
def mockIssue():
    return {
        'key': 'AMDG-FOO',
        'self': "HTTP://fooo",
        'fields': {
            'assignee': {'displayName': 'Dick Whitman'},
            'summary': "I blow up bridges",
            'status': {'name': 'done'},
            'resolution_date': '01/01/1960',
            'aggregatetimespent': 60**2 * 4,
            'timespent': 60**2 * 2,
            'timeestimate': 60**2 * 8,
            'customfield_10143': 8,
            'workratio': 12,
            'subtasks': [1,2,3]
        }
    }


class TestIssueContainer:
    def test_constructs_correctly(self, mockIssue):
        issue_container = IssueContainer(mockIssue)
        for field in issue_container._fields:
            value = getattr(issue_container, field)
            print(field, value)
            assert value
