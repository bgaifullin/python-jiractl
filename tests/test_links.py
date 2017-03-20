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

from jiractl.commands import links

from tests import base


class TestListLinks(base.BaseUnitTest):
    command = links.ListLinks

    def test_success(self):
        self.jira.issue.return_value = mock.Mock(fields=mock.Mock(issuelinks=[mock.Mock()]))
        self.jira.remote_links.return_value = [mock.Mock()]

        self.check_output_many(self.command, ['--issue=ISSUE'], 2)

        self.jira.issue.assert_called_once_with("ISSUE")
        self.jira.remote_links.assert_called_once_with("ISSUE")

    def test_required_arguments(self):
        self.check_required_arguments(self.command, ['--issue=ISSUE'])


class TestAddLink(base.BaseUnitTest):
    command = links.AddLink

    def test_add_issue_link_with_text(self):
        self.jira.create_issue.return_value = mock.Mock()
        argv = ['--issue=ISSUE', '--type=DEPENDS', '--target=TARGET', '--text=TEXT']
        self.check_output_one(self.command, argv)
        self.jira.create_issue_link.assert_called_once_with("DEPENDS", "TARGET", "ISSUE", "TEXT")

    def test_add_issue_link_wo_text(self):
        self.jira.create_issue.return_value = mock.Mock()
        argv = ['--issue=ISSUE', '--type=DEPENDS', '--target=TARGET']
        self.check_output_one(self.command, argv)
        self.jira.create_issue_link.assert_called_once_with("DEPENDS", "TARGET", "ISSUE", None)

    def test_add_remote_link_with_text_and_icon(self):
        self.jira.create_issue.return_value = mock.Mock()
        argv = ['--issue=ISSUE', '--type=link', '--target=TARGET', '--text=TEXT', '--icon=ICON']
        self.check_output_one(self.command, argv)
        self.jira.add_simple_link.assert_called_once_with(
            "ISSUE", {"url": "TARGET", "title": "TEXT", "icon": {"url16x16": "ICON"}}
        )

    def test_add_remote_link_wo_text_and_icon(self):
        self.jira.create_issue.return_value = mock.Mock()
        argv = ['--issue=ISSUE', '--type=link', '--target=http://localhost/path?p=v']
        self.check_output_one(self.command, argv)
        self.jira.add_simple_link.assert_called_once_with(
            "ISSUE",
            {
                "url": "http://localhost/path?p=v",
                "title": "http://localhost/path",
                "icon": {"url16x16": "http://localhost/favicon.ico"}
            }
        )

    def test_required_arguments(self):
        argv = ['--issue=ISSUE', '--type=link', '--target=TARGET']
        self.check_required_arguments(self.command, argv)


class TestShowLink(base.BaseUnitTest):
    command = links.ShowLink

    def test_show_issue_link(self):
        argv = ['--issue=ISSUE', '--id=I1']
        self.check_output_one(self.command, argv)
        self.jira.issue_link.assert_called_once_with("1")
        self.assertEqual(0, self.jira.remote_link.call_count)

    def test_show_remote_link(self):
        argv = ['--issue=ISSUE', '--id=L1']
        self.check_output_one(self.command, argv)
        self.jira.remote_link.assert_called_once_with("ISSUE", "1")
        self.assertEqual(0, self.jira.issue_link.call_count)

    def test_show_fails_if_invalid_id(self):
        argv = ['--issue=ISSUE', '--id=1']
        self.check_stderr(self.command, argv, ValueError, "Link is not found")
        self.assertEqual(0, self.jira.remote_link.call_count)
        self.assertEqual(0, self.jira.issue_link.call_count)

    def test_required_arguments(self):
        argv = ['--issue=ISSUE', '--id=L1']
        self.check_required_arguments(self.command, argv)


class TestDropLink(base.BaseUnitTest):
    command = links.DropLink

    def test_delete_issue_link(self):
        argv = ['--issue=ISSUE', '--id=I1']
        self.check_stdout(self.command, argv, "Done.\n")
        self.jira.delete_issue_link.assert_called_once_with("1")
        self.assertEqual(0, self.jira.remote_link.call_count)

    def test_delete_remote_link(self):
        argv = ['--issue=ISSUE', '--id=L1']
        self.check_stdout(self.command, argv, "Done.\n")
        self.jira.remote_link.assert_called_once_with("ISSUE", "1")
        self.jira.remote_link.return_value.delete.assert_called_once_with()
        self.assertEqual(0, self.jira.delete_issue_link.call_count)

    def test_show_fails_if_invalid_id(self):
        argv = ['--issue=ISSUE', '--id=1']
        self.check_stderr(self.command, argv, ValueError, "Link is not found")
        self.assertEqual(0, self.jira.remote_link.call_count)
        self.assertEqual(0, self.jira.delete_issue_link.call_count)

    def test_required_arguments(self):
        argv = ['--issue=ISSUE', '--id=ID']
        self.check_required_arguments(self.command, argv)
