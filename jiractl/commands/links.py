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


class JiraLinkMixin(object):
    columns = ("id", "type", "text", "details", "icon")

    TYPE_REMOTE_LINK = 'link'

    def get_parser(self, prog_name):
        parser = super(JiraLinkMixin, self).get_parser(prog_name)
        parser.add_argument("--issue", type=base.utf8, help="Issue ID", required=True)
        return parser

    @staticmethod
    def format_issue_link(link):
        """Converts issue link to tuple."""
        try:
            link_target = link.outwardIssue
            link_type = link.type.outward
        except AttributeError:
            link_target = link.inwardIssue
            link_type = link.type.inward

        return (
            "I{0}".format(link.id), link_type, link_target.fields.summary, link_target.fields.status.name, ""
        )

    def format_remote_link(self, link):
        """Converts issue link to tuple."""
        try:
            icon = link.object.icon.url16x16
        except AttributeError:
            icon = ""

        return "L{0}".format(link.id), self.TYPE_REMOTE_LINK, link.object.title, link.object.url, icon


class ListLinks(JiraLinkMixin, base.JiraList):
    """Gets all links for issue."""

    def take_action(self, parsed_args):
        """Get issue by id."""
        issue_links = [self.format_issue_link(x) for x in self.app.jira.issue(parsed_args.issue).fields.issuelinks]
        remote_links = [self.format_remote_link(x) for x in self.app.jira.remote_links(parsed_args.issue)]
        return self.columns, issue_links + remote_links


class AddLink(JiraLinkMixin, base.JiraShow):
    """Adds new link."""

    def get_parser(self, prog_name):
        parser = super(AddLink, self).get_parser(prog_name)
        parser.add_argument("--type", type=base.utf8, help="Link type", required=True)
        parser.add_argument("--target", type=base.utf8, help="Link target, web link or issue ID", required=True)
        parser.add_argument("--text", type=base.utf8, help="Additional text for link")
        parser.add_argument("--icon", type=base.utf8, help="Icon for link, actual only for remote links")

        return parser

    def take_action(self, parsed_args):
        """Adds new link."""
        if parsed_args.type == self.TYPE_REMOTE_LINK:
            data = {
                "url": parsed_args.target,
                "title": parsed_args.text or self._get_title(parsed_args.target),
                "icon": {"url16x16": parsed_args.icon or self._get_favicon(parsed_args.target)},
            }
            link_id = self.app.jira.add_simple_link(parsed_args.issue, data).id
            link = self.format_remote_link(self.app.jira.remote_link(parsed_args.issue, link_id))
        else:
            link_id = self.app.jira.create_issue_link(
                parsed_args.type, parsed_args.target, parsed_args.issue, parsed_args.text
            ).id
            link = self.format_issue_link(self.app.jira.issue_link(parsed_args.issue, link_id))

        return self.columns, link

    @staticmethod
    def _get_title(url):
        data = urlparse.urlparse(url)
        return urlparse.urlunparse((data[0], data[1], data[2], "", "", ""))

    @staticmethod
    def _get_favicon(url):
        data = urlparse.urlparse(url)
        return urlparse.urlunparse((data[0], data[1], "favicon.ico", "", "", ""))


class ShowLink(JiraLinkMixin, base.JiraShow):
    """Shows a link."""

    def get_parser(self, prog_name):
        parser = super(ShowLink, self).get_parser(prog_name)
        parser.add_argument("--id", type=base.utf8, help="Link ID", required=True)
        return parser

    def take_action(self, parsed_args):
        """Get issue by id."""
        if parsed_args.id.startswith("L"):
            data = self.format_remote_link(self.app.jira.remote_link(parsed_args.issue, parsed_args.id[1:]))
        elif parsed_args.id.startswith("I"):
            data = self.format_issue_link(self.app.jira.issue_link(parsed_args.id[1:]))
        else:
            raise ValueError("Link is not found")
        return self.columns, data


class DropLink(JiraLinkMixin, base.JiraCommand):
    def get_parser(self, prog_name):
        parser = super(DropLink, self).get_parser(prog_name)
        parser.add_argument("--id", type=base.utf8, help="Link ID", required=True)
        return parser

    def take_action(self, parsed_args):
        """Get issue by id."""
        if parsed_args.id.startswith("L"):
            self.app.jira.remote_link(parsed_args.issue, parsed_args.id[1:]).delete()
        elif parsed_args.id.startswith("I"):
            self.app.jira.delete_issue_link(parsed_args.id[1:])
        else:
            raise ValueError("Link is not found")
        self.app.stdout.write("Done.\n")
