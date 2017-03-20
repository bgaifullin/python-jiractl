"""
This file is part of jiractl

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import mock

from jiractl.commands import issues

from tests import base


class TestCreateIssue(base.BaseUnitTest):
    command = issues.CreateIssue

    def test_specify_all_arguments(self):
        self.jira.create_issue.return_value = mock.Mock()
        argv = [
            '--project=P1', '--type=T1', '--summary=S1', '--description=D1', '--assignee=USER', '--parent=1',
            '--components', 'C1', 'C2', '--labels', 'L1', 'L2'
        ]
        self.check_output_one(self.command, argv)
        self.jira.create_issue.assert_called_once_with(
            fields={
                "project": "P1", "issuetype": "T1", "summary": "S1", "description": "D1",
                "assignee": {"name": "USER"}, "parent": {"id": "1"},
                "components": [{"name": "C1"}, {"name": "C2"}],
                "labels": ["L1", "L2"],
            },
            prefetch=True
        )

    def test_specify_required_arguments_only(self):
        self.jira.create_issue.return_value = mock.Mock()
        argv = ['--project=P1', '--type=T1', '--summary=S1', '--description=D1']
        self.check_output_one(self.command, argv)
        self.jira.create_issue.assert_called_once_with(
            fields={"project": "P1", "issuetype": "T1", "summary": "S1", "description": "D1"},
            prefetch=True
        )

    def test_required_arguments(self):
        argv = ['--project=P1', '--type=T1', '--summary=S1', '--description=D1']
        self.check_required_arguments(self.command, argv)


class TestEditIssue(base.BaseUnitTest):
    command = issues.EditIssue

    def test_specify_all_arguments(self):
        argv = [
            '--id=1', '--summary=S1', '--description=D1', '--assignee=USER', '--status=WORK',
        ]
        self.check_stdout(self.command, argv, "Done.\n")
        self.jira.issue.assert_called_once_with("1")
        self.jira.issue.return_value.update.assert_called_once_with(fields={"summary": "S1", "description": "D1"})
        self.jira.assign_issue.assert_called_once_with("1", "USER")
        self.jira.transition_issue.assert_called_once_with("1", "WORK")

    def test_specify_required_arguments_only(self):
        argv = ['--id=1']
        self.check_stdout(self.command, argv, "Done.\n")
        self.assertEqual(0, self.jira.issue.call_count)
        self.assertEqual(0, self.jira.assign_issue.call_count)
        self.assertEqual(0, self.jira.transition_issue.call_count)

    def test_update_custom_fields(self):
        argv = ['--id=1', "--fields", "custom_1:value1", "custom_2:value2"]
        self.check_stdout(self.command, argv, "Done.\n")
        self.jira.issue.return_value.update.assert_called_once_with(
            fields={"custom_1": "value1", "custom_2": "value2"}
        )
        self.assertEqual(0, self.jira.assign_issue.call_count)
        self.assertEqual(0, self.jira.transition_issue.call_count)

    def test_required_arguments(self):
        argv = ['--id=1']
        self.check_required_arguments(self.command, argv)


class TestShowIssue(base.BaseUnitTest):
    command = issues.ShowIssue

    def test_success(self):
        argv = ['--id=1']
        self.check_output_one(self.command, argv)
        self.jira.issue.assert_called_once_with("1")

    def test_show_with_custom_column(self):
        argv = ['--id=1', '-c', 'custom_1']
        columns = self.command.columns + ("custom_1",)
        expected_data = (mock.ANY,) * len(columns)
        self.check_output(self.command, argv, expected_data, columns=columns)
        self.jira.issue.assert_called_once_with("1")

    def test_required_arguments(self):
        argv = ['--id=1']
        self.check_required_arguments(self.command, argv)


class TestListIssues(base.BaseUnitTest):
    command = issues.ListIssues

    def test_success(self):
        self.jira.search_issues.return_value = [mock.Mock(), mock.Mock()]
        self.check_output_many(self.command, ['--project=P1', '--assigne=USER', '--status', 'NEW', 'WORK'], 2)
        self.jira.search_issues.assert_called_once_with(
            'project="P1" AND assignee="USER" AND status IN ("NEW","WORK")'
        )

    def test_required_arguments(self):
        self.check_required_arguments(self.command, ['--project=P1', '--assigne=USER', '--status=NEW'])


class TestSearchIssues(base.BaseUnitTest):
    command = issues.SearchIssues

    def test_success(self):
        self.jira.search_issues.return_value = [mock.Mock(), mock.Mock()]
        self.check_output_many(self.command, ['--query', 'project="P1" AND assignee="USER"'], 2)
        self.jira.search_issues.assert_called_once_with('project="P1" AND assignee="USER"')

    def test_required_arguments(self):
        self.check_required_arguments(self.command, ['--query=project="P1"'])
