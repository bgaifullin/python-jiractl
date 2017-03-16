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

from cliff import app
from cliff.commandmanager import CommandManager
import jira

import jiractl


class JiraApp(app.App):
    """Main cliff application class.

    Performs initialization of the command manager and
    configuration of basic engines.
    """

    _jira = None

    def build_option_parser(self, description, version, argparse_kwargs=None):
        """Specifies global options."""
        parser = super(JiraApp, self).build_option_parser(
            description=description, version=version, argparse_kwargs=argparse_kwargs
        )

        parser.add_argument(
            "-s", "--server",
            metavar="URL",
            help="The Jira URL",
        )
        parser.add_argument(
            "-u", "--user",
            metavar="USERNAME",
            help="Jira user"
        )
        parser.add_argument(
            "-p", "--password",
            metavar="PASSWORD",
            help="Jira password"
        )
        return parser

    @property
    def jira(self):
        if self._jira is None:
            self._jira = jira.JIRA(server=self.options.server, basic_auth=(self.options.user, self.options.password))
        return self._jira


def run_app(cmd_mgr, argv=None):
    """Runs application."""
    return JiraApp(
        description="The command line interface for Jira REST API",
        version=jiractl.__version__,
        command_manager=cmd_mgr,
        deferred_help=True
    ).run(argv)


def main(argv=None):
    """Entry point."""
    return run_app(CommandManager(__package__, convert_underscores=True), argv)


def debug(name, cmd_class, argv=None):
    """Helper for debugging single command without package installation."""
    import sys

    if argv is None:
        argv = sys.argv[1:]

    argv = [name] + argv + ["-v", "-v", "--debug"]
    cmd_mgr = CommandManager(__package__, convert_underscores=True)
    cmd_mgr.add_command(name, cmd_class)

    return run_app(cmd_mgr, argv)
