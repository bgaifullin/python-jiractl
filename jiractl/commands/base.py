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

from cliff import command
from cliff import lister
from cliff import show


def utf8(text):
    """Converts text to utf8 encoded string"""
    return unicode(text, "utf8")


class JiraCommand(command.Command):
    """Executes command."""


class JiraShow(show.ShowOne):
    """Executes command and displays result for one element."""


class JiraList(lister.Lister):
    """Executes command and displays list of elements."""
