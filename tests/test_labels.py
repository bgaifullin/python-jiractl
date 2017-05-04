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

from jiractl.commands import labels

from tests import base


class TestListLabels(base.BaseUnitTest):
    command = labels.ListLabels

    def test_success(self):
        self.jira.issue.return_value = mock.Mock(fields=mock.Mock(labels=["label1"]))
        self.check_output_many(self.command, ['--issue=ISSUE'], 1)

        self.jira.issue.assert_called_once_with("ISSUE")

    def test_required_arguments(self):
        self.check_required_arguments(self.command, ['--issue=ISSUE'])


class TestAddLabels(base.BaseUnitTest):
    command = labels.AddLabel

    def test_add_existed_label(self):
        self.jira.issue.return_value = mock.Mock(fields=mock.Mock(labels=["label1"]))
        argv = ['--issue=ISSUE', '--labels=label1']
        self.check_stdout(self.command, argv, "Done.\n")
        self.jira.issue.assert_called_once_with("ISSUE")
        self.assertEqual(0, self.jira.issue.return_value.update.call_count)

    def test_add_new_label(self):
        self.jira.issue.return_value = mock.Mock(fields=mock.Mock(labels=[]))
        argv = ['--issue=ISSUE', '--labels=label1']
        self.check_stdout(self.command, argv, "Done.\n")
        self.jira.issue.assert_called_once_with("ISSUE")
        self.jira.issue.return_value.update.assert_called_once_with(fields={"labels": ["label1"]})

    def test_add_labels(self):
        self.jira.issue.return_value = mock.Mock(fields=mock.Mock(labels=["label1", "label2"]))
        argv = ['--issue=ISSUE', '--labels', 'label2', 'label3']
        self.check_stdout(self.command, argv, "Done.\n")
        self.jira.issue.assert_called_once_with("ISSUE")
        self.jira.issue.return_value.update.assert_called_once_with(fields={"labels": ["label1", "label2", "label3"]})

    def test_required_arguments(self):
        argv = ['--issue=ISSUE', '--labels=label']
        self.check_required_arguments(self.command, argv)


class TestDropLabels(base.BaseUnitTest):
    command = labels.DropLabel

    def test_delete_non_existed_labels(self):
        self.jira.issue.return_value = mock.Mock(fields=mock.Mock(labels=["label2"]))
        argv = ['--issue=ISSUE', '--labels', 'label1']
        self.check_stdout(self.command, argv, "Done.\n")
        self.jira.issue.assert_called_once_with("ISSUE")
        self.assertEqual(0, self.jira.issue.return_value.update.call_count)

    def test_delete_labels(self):
        self.jira.issue.return_value = mock.Mock(fields=mock.Mock(labels=["label1", "label2"]))
        argv = ['--issue=ISSUE', '--labels', 'label2', 'label3']
        self.check_stdout(self.command, argv, "Done.\n")
        self.jira.issue.assert_called_once_with("ISSUE")
        self.jira.issue.return_value.update.assert_called_once_with(fields={"labels": ["label1"]})

    def test_required_arguments(self):
        argv = ['--issue=ISSUE', '--labels=label']
        self.check_required_arguments(self.command, argv)
