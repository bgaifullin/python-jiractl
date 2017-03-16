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

from jiractl.commands import base


class JiraIssueMixin(object):
    columns = ("project", "id", "key", "summary", "type", "assignee", "status")

    @staticmethod
    def format_issue(issue):
        """Converts issue to tuple."""
        return (
            issue.fields.project.name, issue.id, issue.key, issue.fields.summary,
            issue.fields.issuetype.name, issue.fields.assignee.name, issue.fields.status.name,
        )


class CreateIssue(JiraIssueMixin, base.JiraShow):
    """Creates issue"""

    def get_parser(self, prog_name):
        parser = super(CreateIssue, self).get_parser(prog_name)
        parser.add_argument("--project", type=base.utf8, help="Jira project", required=True)
        parser.add_argument("--type", type=base.utf8, help="Issue Type", required=True)
        parser.add_argument("--summary", type=base.utf8, help="Issue Summary", required=True)
        parser.add_argument("--description", type=base.utf8, help="Issue description", required=True)
        parser.add_argument("--assignee", type=base.utf8, help="Issue Assignee")
        parser.add_argument("--parent", type=base.utf8, help="Issue parent")
        parser.add_argument("--components", type=base.utf8, nargs='+', help="Issue component")
        parser.add_argument("--labels", type=base.utf8, nargs='+', help="Issue label")

        return parser

    def take_action(self, parsed_args):
        """Creates a new jira issue."""
        fields = {
            "project": parsed_args.project,
            "issuetype": parsed_args.type,
            "summary": parsed_args.summary,
            "description": parsed_args.description
        }
        if parsed_args.assignee:
            fields["assignee"] = parsed_args.assignee
        if parsed_args.labels:
            fields["assignee"] = {"name": parsed_args.assignee}
        if parsed_args.parent:
            fields["parent"] = {"id": parsed_args.parent}
        if parsed_args.components:
            fields["components"] = [{'name': c} for c in parsed_args.components]
        if parsed_args.labels:
            fields["labels"] = parsed_args.labels

        return self.columns, self.format_issue(self.app.jira.create_issue(fields=fields, prefetch=True))


class EditIssue(JiraIssueMixin, base.JiraCommand):
    """Updates issue"""

    def get_parser(self, prog_name):
        parser = super(EditIssue, self).get_parser(prog_name)
        parser.add_argument("--id", type=base.utf8, help="Issue ID", required=True)
        parser.add_argument("--summary", type=base.utf8, help="New issue Summary")
        parser.add_argument("--description", type=base.utf8, help="New issue description")
        parser.add_argument("--assignee", type=base.utf8, help="New issue assignee")
        parser.add_argument("--status", type=base.utf8, help="Transition issue to status")

        return parser

    def take_action(self, parsed_args):
        """Update issue."""
        fields = {}
        if parsed_args.summary:
            fields["summary"] = parsed_args.summary
        if parsed_args.description:
            fields["description"] = parsed_args.description

        if fields:
            self.app.jira.issue(parsed_args.id).update(fields=fields)

        if parsed_args.assignee:
            self.app.jira.assign_issue(parsed_args.id, parsed_args.assignee)

        if parsed_args.status:
            self.app.jira.transition_issue(parsed_args.id, parsed_args.status)

        self.app.stdout.write("Done.\n")


class ShowIssue(JiraIssueMixin, base.JiraShow):
    """Updates issue"""

    def get_parser(self, prog_name):
        parser = super(ShowIssue, self).get_parser(prog_name)
        parser.add_argument("--id", type=base.utf8, help="Issue ID", required=True)
        return parser

    def take_action(self, parsed_args):
        """Get issue by id."""
        return self.columns, self.format_issue(self.app.jira.issue(parsed_args.id))


class ListIssues(JiraIssueMixin, base.JiraList):
    """Get list of issues which match specified criteria."""

    def get_parser(self, prog_name):
        parser = super(ListIssues, self).get_parser(prog_name)
        parser.add_argument("--project", type=base.utf8, help="Jira project", required=True)
        parser.add_argument("--assignee", type=base.utf8, help="Issue assignee", required=True)
        parser.add_argument("--status", type=base.utf8, nargs='+', help="Issue status", required=True)
        return parser

    def take_action(self, parsed_args):
        """Gets issues."""
        query = u'project="{0}" AND assignee="{1}" AND status IN ("{2}")'.format(
            parsed_args.project, parsed_args.assignee, u'","'.join(x for x in parsed_args.status)
        )
        issues = self.app.jira.search_issues(query)
        return self.columns, [self.format_issue(issue) for issue in issues]


class SearchIssues(JiraIssueMixin, base.JiraList):
    """Searches issues by Jira Query string."""
    def get_parser(self, prog_name):
        parser = super(SearchIssues, self).get_parser(prog_name)
        parser.add_argument("--query", type=base.utf8, help="Query string", required=True)
        return parser

    def take_action(self, parsed_args):
        """Searches issues."""
        issues = self.app.jira.search_issues(parsed_args.query)
        return self.columns, [self.format_issue(issue) for issue in issues]
