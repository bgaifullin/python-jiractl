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

from jiractl.commands import comments

from tests import base


class TestListComments(base.BaseUnitTest):
    command = comments.ListComments

    def test_success(self):
        self.jira.comments.return_value = [mock.Mock(), mock.Mock()]
        self.check_output_many(self.command, ['--issue=ISSUE'], 2)
        self.jira.comments.assert_called_once_with("ISSUE")

    def test_required_arguments(self):
        self.check_required_arguments(self.command, ['--issue=ISSUE'])


class TestAddComment(base.BaseUnitTest):
    command = comments.AddComment

    def test_specify_all_arguments(self):
        self.jira.create_issue.return_value = mock.Mock()
        argv = ['--issue=ISSUE', '--text=TEXT1<br>TEXT2', '--visibility=TYPE:VALUE']
        self.check_output_one(self.command, argv)
        self.jira.add_comment.assert_called_once_with(
            "ISSUE", "TEXT1\nTEXT2", visibility={"type": "TYPE", "value": "VALUE"}
        )

    def test_specify_required_arguments_only(self):
        self.jira.create_issue.return_value = mock.Mock()
        argv = ['--issue=ISSUE', '--text=TEXT']
        self.check_output_one(self.command, argv)
        self.jira.add_comment.assert_called_once_with("ISSUE", "TEXT", visibility=None)

    def test_required_arguments(self):
        argv = ['--issue=ISSUE', '--text=TEXT']
        self.check_required_arguments(self.command, argv)


class TestEditComment(base.BaseUnitTest):
    command = comments.EditComment

    def test_specify_all_arguments(self):
        argv = ['--issue=ISSUE', '--id=1', '--text=TEXT1<br>TEXT2', '--visibility=TYPE:VALUE']
        self.check_stdout(self.command, argv, "Done.\n")
        self.jira.comment.assert_called_once_with("ISSUE", "1")
        self.jira.comment.return_value.update.assert_called_once_with(
            body="TEXT1\nTEXT2", visibility={"type": "TYPE", "value": "VALUE"}
        )

    def test_specify_required_arguments_only(self):
        argv = ['--issue=ISSUE', '--id=1', '--text=TEXT']
        self.check_stdout(self.command, argv, "Done.\n")
        self.jira.comment.assert_called_once_with("ISSUE", "1")
        self.jira.comment.return_value.update.assert_called_once_with(body="TEXT", visibility=None)

    def test_required_arguments(self):
        argv = ['--issue=ISSUE', '--id=1']
        self.check_required_arguments(self.command, argv)


class TestShowComment(base.BaseUnitTest):
    command = comments.ShowComment

    def test_success(self):
        argv = ['--issue=ISSUE', '--id=1']
        self.check_output_one(self.command, argv)
        self.jira.comment.assert_called_once_with("ISSUE", "1")

    def test_required_arguments(self):
        argv = ['--issue=ISSUE', '--id=1']
        self.check_required_arguments(self.command, argv)
