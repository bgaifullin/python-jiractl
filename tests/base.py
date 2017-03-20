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
import unittest

from jiractl import app


class BaseUnitTest(unittest.TestCase):

    def setUp(self):
        m = mock.patch('jiractl.app.JiraApp.jira')
        self.jira = m.start()
        self.addCleanup(self.jira.stop)
        m = mock.patch('sys.stderr')
        self.stderr = m.start()
        self.addCleanup(self.stderr.stop)
        m = mock.patch('sys.stdout')
        self.stdout = m.start()
        self.addCleanup(self.stdout.stop)

    @staticmethod
    def check_output(command, argv, expected_data, columns=None):
        with mock.patch.object(command, 'produce_output') as output_mock:
            app.debug("command", command, argv)

        # parsed_args, columns, data
        output_mock.assert_called_once_with(mock.ANY, columns or command.columns, expected_data)

    def check_output_one(self, command, argv):
        expected_data = (mock.ANY,) * len(command.columns)
        return self.check_output(command, argv, expected_data)

    def check_output_many(self, command, argv, count):
        expected_data = [(mock.ANY,) * len(command.columns)] * count
        return self.check_output(command, argv, expected_data)

    def check_stdout(self, command, argv, message):
        app.debug("command", command, argv)
        self.assertIn(message, self.stdout.write.call_args[0][0])

    def check_stderr(self, command, argv, exc, message):
        self.assertRaises(exc, app.debug, "command", command, argv)
        self.assertIn(message, self.stderr.write.call_args[0][0])

    def check_required_arguments(self, command, argv):
        for i in range(len(argv)):
            argv2 = argv[:]
            del argv2[i]
            self.check_stderr(command, argv2, SystemExit, argv[i].split('=')[0])
            self.stderr.reset_mock()
