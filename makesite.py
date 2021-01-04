#!/usr/bin/env python

# BSD 3-Clause License
#
# Copyright (c) 2020, Timothy Trippel <trippel@umich.edu>
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
import datetime
import glob
import json
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


def truncate(text, words=25):
    """Remove tags and truncate text to the specified number of words."""
    return ' '.join(re.sub('(?s)<.*?>', ' ', text).split()[:words])


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
        'date_month': calendar.month_abbr[int(match.group(3) or '01')],
        'date_day': int(match.group(4) or '01'),
        'slug': match.group(5),
    }

    # Read headers.
    end = 0
    for key, val, end in read_headers(text):
        content[key] = val

    # Separate content from headers.
    text = text[end:]

    # Convert Markdown content to HTML.
    if filename.endswith(('.md', '.mkd', '.mkdn', '.mdown', '.markdown')):
        text = markdown_2_html(filename, text)

    # # Update the dictionary with content and RFC 2822 date.
    content.update({
        'content': text,
        # 'rfc_2822_date': rfc_2822_format(content['date'])
    })

    return content


def render(template, **params):
    """Replace placeholders in template with values from params."""
    return re.sub(
        r'{{\s*([^}\s]+)\s*}}',
        lambda match: str(params.get(match.group(1), match.group(0))),
        template)


def make_pages(src, dst, layout, **params):
    """Generate pages from page content."""
    items = []

    for src_path in glob.glob(src):
        content = read_content(src_path)

        page_params = dict(params, **content)

        # Populate placeholders in content if content-rendering is enabled.
        if page_params.get('render') == 'yes':
            rendered_content = render(page_params['content'], **page_params)
            page_params['content'] = rendered_content
            content['content'] = rendered_content

        items.append(content)

        dst_path = render(dst, **page_params)
        output = render(layout, **page_params)

        log('Rendering {} => {} ...', src_path, dst_path)
        fwrite(dst_path, output)

    return sorted(items, key=lambda x: x['date'], reverse=True)


def make_index(src, dst_path, homepage_layout, news_item_layout, **params):
    """Generate homepage from content."""
    # Create deepcopy of params
    page_params = dict(params)

    # Render homepage header with bio and interests
    news_src = None
    for src_path in glob.glob(src):
        # if we encounter news/ sub-directory, save the path
        if os.path.isdir(src_path) and os.path.basename(src_path) == "news":
            news_src = os.path.join(src_path, "*.md")
            continue
        content = read_content(src_path)
        page_params[content['slug']] = content['content']
        log('Rendering {} => {} ...', src_path, dst_path)

    # Extract news items
    news_content = []
    for src_path in glob.glob(news_src):
        content = read_content(src_path)
        news_content.append(content)
    news_content.sort(key=lambda x: x['date'], reverse=True)

    # Render news item HTML
    news_items = []
    for content in news_content:
        page_params.update(content)
        log('Rendering {} => {} ...', src_path, dst_path)
        news_item = render(news_item_layout, **page_params)
        news_items.append(news_item)
    page_params['news'] = ''.join(news_items)

    # Render homepage and write to file
    output = render(homepage_layout, **page_params)
    fwrite(dst_path, output)


def make_publications(src, dst_path, publications_layout, **params):
    """Generate publications page from content."""
    pub_contents = []

    # Create deepcopy of params (to enable safe modification)
    page_params = dict(params)

    # Extract publication items
    pub_items = []
    for pub_file in glob.glob(os.path.join(src, "*.html")):
        pub_items.append(read_content(pub_file))
    pub_items.sort(key=lambda x: x['date'], reverse=True)

    # Render publication items and combine into HTML string
    for pub_item in pub_items:
        page_params.update(pub_item)
        rendered_content = render(page_params['content'], **page_params)
        pub_contents.append(rendered_content)

    # Write publications HTML to file
    page_params['content'] = ''.join(pub_contents)
    output = render(publications_layout, **page_params)
    fwrite(dst_path, output)


def make_experience(src, dst_path, experience_layout, experience_item_layout,
                    **params):
    """Generate experience page from content."""
    exp_contents = []

    # Create deepcopy of params (to enable safe modification)
    page_params = dict(params)

    # Extract past experience items
    exp_items = []
    for exp_file in glob.glob(os.path.join(src, "past", "*.md")):
        exp_items.append(read_content(exp_file))
    exp_items.sort(key=lambda x: (x["end_year"], x["end_month"]), reverse=True)

    # Render experience items and combine into HTML string
    for exp_item in exp_items:
        rendered_content = render(experience_item_layout, **exp_item)
        exp_contents.append(rendered_content)

    # Write experience HTML to file
    page_params["content"] = "".join(exp_contents)
    output = render(experience_layout, **page_params)
    fwrite(dst_path, output)


# def make_list(posts, dst, list_layout, item_layout, **params):
# """Generate list page for a blog."""
# items = []
# for post in posts:
# item_params = dict(params, **post)
# item_params['summary'] = truncate(post['content'])
# item = render(item_layout, **item_params)
# items.append(item)

# params['content'] = ''.join(items)
# dst_path = render(dst, **params)
# output = render(list_layout, **params)

# log('Rendering list => {} ...', dst_path)
# fwrite(dst_path, output)


def main():
    # Create a new _site directory from scratch.
    if os.path.isdir('_site'):
        shutil.rmtree('_site')
    shutil.copytree('static', '_site')

    # Default parameters.
    params = {
        'base_path': '/Users/ttrippel/repos/mywebsite/_site',
        'subtitle': 'Personal Website',
        'author': 'Timothy Trippel',
        'site_url': 'http://localhost:8000',
        'current_year': datetime.datetime.now().year,

        # Student Info
        'phd_student_status': 'Candidate',
        'laboratory_name': 'RTCL Laboratory',
        'university_department': 'Computer Science & Engineering',
        'university': 'University of Michigan',

        # Social Media
        'twitter_username': 'TimothyTrippel',
        'github_username': 'timothytrippel',
        'linkedin_user_id': 'timothy-trippel-98a95657',
        'google_scholar_user_id': 'PZOHIxAAAAAJ',

        # CV
        'cv_file_name': 'timothy_trippel_cv.pdf',

        # TODO(timothytrippel): move to header comments of hompage.html layout
        # Hompage (index.html)
        'author_photo': 'timothytrippel.jpg',
        # Contact Info.
        'address_line_1': '4944 Bob & Betty Beyster Building',
        'address_line_2': '2260 Hayward St.',
        'address_line_3': 'Ann Arbor, MI 48109',
        'email_username': 'trippel',
        'email_hostname': 'umich.edu',
        # Education Info.
        'expected_graduation_month': 'May',
        'expected_graduation_year': 2021,
    }

    # If params.json exists, load it.
    if os.path.isfile('params.json'):
        params.update(json.loads(fread('params.json')))

    # Load layouts.
    page_layout = fread('layout/page.html')
    nav_layout = fread('layout/nav.html')
    index_layout = fread('layout/index.html')
    news_item_layout = fread('layout/news_item.html')
    publications_layout = fread('layout/publications.html')
    experience_layout = fread('layout/experience.html')
    experience_item_layout = fread('layout/experience_item.html')

    # Combine layouts to form final layouts.
    page_layout = render(page_layout, navbar=nav_layout)
    index_layout = render(page_layout, content=index_layout)
    publications_layout = render(page_layout, content=publications_layout)
    experience_layout = render(page_layout, content=experience_layout)

    # Create site pages.
    make_index('content/index/*',
               '_site/index.html',
               index_layout,
               news_item_layout,
               render='yes',
               **params)
    make_publications('content/publications', '_site/publications.html',
                      publications_layout, **params)
    make_experience('content/experience',
                    '_site/experience.html',
                    experience_layout,
                    experience_item_layout,
                    render='yes',
                    **params)


# Test parameter to be set temporarily by unit tests.
_test = None

if __name__ == '__main__':
    main()
