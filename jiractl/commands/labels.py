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

import urlparse

from jiractl.commands import base


class JiraLabelMixin(object):
    columns = "label",

    def get_parser(self, prog_name):
        parser = super(JiraLabelMixin, self).get_parser(prog_name)
        parser.add_argument("--issue", type=base.utf8, help="Issue ID", required=True)
        return parser


class ListLabels(JiraLabelMixin, base.JiraList):
    """Gets all labels for issue."""

    def take_action(self, parsed_args):
        """Get issue by id."""

        return self.columns, [(x,) for x in self.app.jira.issue(parsed_args.issue).fields.labels]


class AddLabel(JiraLabelMixin, base.JiraCommand):
    """Adds new link."""

    def get_parser(self, prog_name):
        parser = super(AddLabel, self).get_parser(prog_name)
        parser.add_argument("--labels", type=base.utf8, nargs='+', required=True, help="Label text")
        return parser

    def take_action(self, parsed_args):
        """Adds new link."""
        issue = self.app.jira.issue(parsed_args.issue)
        labels = issue.fields.labels
        missing = set(parsed_args.labels).difference(labels)
        if missing:
            issue.update(fields={'labels': labels + sorted(missing)})

        self.app.stdout.write("Done.\n")


class DropLabel(JiraLabelMixin, base.JiraCommand):
    def get_parser(self, prog_name):
        parser = super(DropLabel, self).get_parser(prog_name)
        parser.add_argument("--labels", type=base.utf8, nargs='+', required=True, help="Label text")
        return parser

    def take_action(self, parsed_args):
        """Get issue by id."""
        issue = self.app.jira.issue(parsed_args.issue)
        labels = set(issue.fields.labels).difference(parsed_args.labels)
        if len(labels) != len(issue.fields.labels):
            issue.update(fields={'labels': sorted(labels)})

        self.app.stdout.write("Done.\n")
