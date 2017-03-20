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


class JiraCommentMixin(object):
    columns = ("id", "updated", "author", "text")

    def get_parser(self, prog_name):
        parser = super(JiraCommentMixin, self).get_parser(prog_name)
        parser.add_argument("--issue", type=base.utf8, help="Issue ID", required=True)
        return parser

    @staticmethod
    def format_comment(comment):
        """Converts issue comment to tuple."""
        return comment.id, comment.updated,  comment.author.name, comment.body

    @staticmethod
    def format_text(text):
        """Formats text."""
        return text.replace("<br>", "\n")


class ListComments(JiraCommentMixin, base.JiraList):
    """Gets all comments for issue."""

    def take_action(self, parsed_args):
        """Get issue by id."""
        return self.columns, [self.format_comment(x) for x in self.app.jira.comments(parsed_args.issue)]


class AddComment(JiraCommentMixin, base.JiraShow):
    """Adds new comment."""

    def get_parser(self, prog_name):
        parser = super(AddComment, self).get_parser(prog_name)
        parser.add_argument("--text", type=base.utf8, help="Comment", required=True)
        parser.add_argument(
            "--visibility", type=base.utf8, metavar="TYPE:VALUE", help="Visibility of issue. format %(metavar)"
        )
        return parser

    def take_action(self, parsed_args):
        """Adds new comment."""
        visibility = None
        if parsed_args.visibility:
            visibility = dict(zip(("type", "value"), parsed_args.visibility.split(":", 2)))

        comment = self.app.jira.add_comment(
            parsed_args.issue, self.format_text(parsed_args.text), visibility=visibility
        )
        return self.columns, self.format_comment(comment)


class EditComment(JiraCommentMixin, base.JiraCommand):
    """Edit comment."""

    def get_parser(self, prog_name):
        parser = super(EditComment, self).get_parser(prog_name)
        parser.add_argument("--id", type=base.utf8, help="Comment ID", required=True)
        parser.add_argument("--text", type=base.utf8, help="Comment", required=True)
        parser.add_argument("--visibility", type=base.utf8, help="Visibility in format type:value")
        return parser

    def take_action(self, parsed_args):
        """Get issue by id."""
        visibility = None
        if parsed_args.visibility:
            visibility = dict(zip(("type", "value"), parsed_args.visibility.split(":", 2)))

        comment = self.app.jira.comment(parsed_args.issue, parsed_args.id)
        comment.update(body=self.format_text(parsed_args.text), visibility=visibility)
        self.app.stdout.write("Done.\n")


class ShowComment(JiraCommentMixin, base.JiraShow):
    """Shows one comment."""

    def get_parser(self, prog_name):
        parser = super(ShowComment, self).get_parser(prog_name)
        parser.add_argument("--id", type=base.utf8, help="Comment ID", required=True)
        return parser

    def take_action(self, parsed_args):
        """Get issue by id."""
        return self.columns, self.format_comment(self.app.jira.comment(parsed_args.issue, parsed_args.id))
