#!/usr/bin/env python

# BSD 3-Clause License
#
# Copyright (c) 2021, Timothy Trippel <trippel@umich.edu>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permisson.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# This software is a derivative of the original makesite.py.
# The license text of the original makesite.py is included below.
#
# The MIT License (MIT)
#
# Copyright (c) 2018 Sunaina Pai
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""Make static personal website with Python."""

import calendar
import collections
import datetime
import glob
import os
import re
import shutil
import sys

import hjson


def fread(filename):
    """Read file and close the file."""
    with open(filename, 'r') as f:
        return f.read()


def fwrite(filename, text):
    """Write content to file and close the file."""
    basedir = os.path.dirname(filename)
    if not os.path.isdir(basedir):
        os.makedirs(basedir)

    with open(filename, 'w') as f:
        f.write(text)


def log(msg, *args):
    """Log message with specified arguments."""
    sys.stderr.write(msg.format(*args) + '\n')


def read_headers(text):
    """Parse headers in text and yield (key, value, end-index) tuples."""
    for match in re.finditer(r'\s*<!--\s*(.+?)\s*:\s*(.+?)\s*-->\s*|.+', text):
        if not match.group(1):
            break
        yield match.group(1), match.group(2), match.end()


def rfc_2822_format(date_str):
    """Convert yyyy-mm-dd date string to RFC 2822 format date string."""
    d = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    return d.strftime('%a, %d %b %Y %H:%M:%S +0000')


def markdown_2_html(filename, text):
    """Convert markdown text string to an HTML text string."""
    try:
        if _test == 'ImportError':
            raise ImportError('Error forced by test')
        import commonmark
        text = commonmark.commonmark(text)
    except ImportError as e:
        log('WARNING: Cannot render Markdown in {}: {}', filename, str(e))
    return text


def read_content(filename):
    """Read content and metadata from file into a dictionary."""
    # Read file content.
    text = fread(filename)

    # Read metadata and save it in a dictionary.
    date_slug = os.path.basename(filename).split('.')[0]
    match = re.search(r'^(?:((\d\d\d\d)-(\d\d)-(\d\d))-)?(.+)$', date_slug)
    content = {
        'date': match.group(1) or '1970-01-01',
        'date_year': int(match.group(2) or '1970'),
        'date_month': int(match.group(3) or '01'),
        'date_month_abbr': calendar.month_abbr[int(match.group(3) or '01')],
        'date_day': int(match.group(4) or '01'),
        'slug': match.group(5),
    }

    # Update format of month abbreviation.
    if len(calendar.month_name[content["date_month"]]) > 3:
        if content["date_month_abbr"] == "Sep":
            content["date_month_abbr"] += "t"
        content["date_month_abbr"] += "."

    # Read headers.
    end = 0
    for key, val, end in read_headers(text):
        content[key] = val

    # Separate content from headers.
    text = text[end:]

    # Convert Markdown content to HTML.
    if filename.endswith(('.md', '.mkd', '.mkdn', '.mdown', '.markdown')):
        text = markdown_2_html(filename, text)

    # Update the dictionary with content and RFC 2822 date.
    content.update({
        'content': text,
        # TODO(timothytrippel): uncomment this
        # 'rfc_2822_date': rfc_2822_format(content['date'])
    })

    return content


def render(template, **params):
    """Replace placeholders in template with values from params."""
    return re.sub(
        r'{{\s*([^}\s]+)\s*}}',
        lambda match: str(params.get(match.group(1), match.group(0))),
        template)


def make_list(src, item_layout, key, params):
    """Generate HTML list string from several (HTML/Markdown) content files."""
    # Extract content from content files
    items = []
    for content_file in glob.glob(src):
        item_params = read_content(content_file)
        # render any placeholders in the content itself
        item_params["content"] = render(item_params["content"], **params)
        items.append(item_params)

    # Sort items by date
    items.sort(key=lambda x: (x["date_year"], x["date_month"], x["date_day"]),
               reverse=True)

    # Render items and build HTML string
    html_strs = []
    num_item_types = collections.defaultdict(int)
    for item_params in items:
        log("Rendering list item => {}-{} ...", item_params["date"],
            item_params["slug"])
        # Count sub-types within a list (for publications)
        if "type" in item_params:
            num_item_types["num_%s" % item_params["type"]] += 1
        # Combine content with a pre-defined HTML layout
        if item_layout is not None:
            item_html_str = render(item_layout, **item_params)
        # Content is the HTML string itself
        else:
            item_html_str = render(item_params["content"], **item_params)
        html_strs.append(item_html_str)
    params["num_list_items"] = len(items)
    params.update(num_item_types)
    params[key] = "".join(html_strs)


def make_page(slug, layouts, **params):
    """Generate website page from layout and content directory."""
    # Create deepcopy of params
    page_params = dict(params)

    # Create src and dst paths
    content_glob = os.path.join("content", slug, "*")
    dst_path = os.path.join(params["base_path"], slug + ".html")

    # Render page with content from the content directory
    # Content directory contains only content that will form a list
    if params.get("list_only") is True:
        make_list(content_glob, None, "content", page_params)
    # Content directory contains singular and listable content
    else:
        for src_path in glob.glob(content_glob):
            # if we encounter a sub-directory, make a list from content files
            if os.path.isdir(src_path):
                param = os.path.basename(src_path)
                make_list(os.path.join(src_path, "*"), layouts[param], param,
                          page_params)
            # Otherwise, content file will fill the placeholder in the
            # layout with the same name as the content file slug
            else:
                content = read_content(src_path)
                rendered_content = render(content["content"], **page_params)
                page_params[content["slug"]] = rendered_content

    # Render homepage and write to file
    log('Rendering {} page => {}.html ...', slug, slug)
    output = render(layouts[slug], **page_params)
    fwrite(dst_path, output)


def load_layouts(src, **params):
    """Load layouts into a dictionary with slugs as a key."""
    layouts = {}
    for layout_file in glob.glob(os.path.join(src, "*", "*.html")):
        slug = os.path.basename(layout_file)[:-5]
        layouts[slug] = fread(layout_file)
    return layouts


def main():
    # Create a new _site directory from scratch.
    if os.path.isdir("_site"):
        shutil.rmtree("_site")
    shutil.copytree("static", "_site")

    # Default parameters.
    params = {
        "base_path": "/Users/ttrippel/repos/mywebsite/_site",
        "site_url": "http://localhost:8000",
        "current_year": datetime.datetime.now().year,
    }

    # If params.hjson exists, load it.
    if os.path.isfile('params.hjson'):
        params.update(hjson.loads(fread('params.hjson')))

    # Load layouts.
    layouts = load_layouts("layout")

    # Combine layouts to form final layouts.
    # Base page layout.
    layouts["page"] = render(layouts["page"], nav=layouts["nav"])
    # List item layouts.
    layouts["past_jobs"] = render(layouts["past_jobs"],
                                  content=layouts["jobs"])
    layouts["current_jobs"] = render(layouts["current_jobs"],
                                     content=layouts["jobs"])
    # Layouts of each page.
    # TODO(timothytrippel): refactor setting the class of the current page to
    # highlight the correct menu-item in the navbar. This is ugly ...
    layouts["index"] = render(layouts["page"],
                              content=layouts["index"],
                              menu_item_index_class="currentmenu",
                              menu_item_publications_class="",
                              menu_item_experience_class="")
    layouts["publications"] = render(
        layouts["page"],
        content=layouts["publications"],
        menu_item_index_class="",
        menu_item_publications_class="currentmenu",
        menu_item_research_class="",
        menu_item_experience_class="")
    layouts["experience"] = render(layouts["page"],
                                   content=layouts["experience"],
                                   menu_item_index_class="",
                                   menu_item_publications_class="",
                                   menu_item_research_class="",
                                   menu_item_experience_class="currentmenu")
    layouts["research"] = render(layouts["page"],
                                 content=layouts["research"],
                                 menu_item_index_class="",
                                 menu_item_publications_class="",
                                 menu_item_research_class="currentmenu",
                                 menu_item_experience_class="")

    # Create site pages.
    make_page("index", layouts, **params)
    make_page("experience", layouts, **params)
    make_page("publications", layouts, list_only=True, **params)
    make_page("research", layouts, **params)


# Test parameter to be set temporarily by unit tests.
_test = None

if __name__ == '__main__':
    main()
