# mywebsite ([https://timothytrippel.com](https://timothytrippel.com))

A simple Python-generated static website tailored for Ph.D. students and/or
academics with active research projects and/or publication lists. See link above
for the deployed final product.

# Getting Started

This repository contains a static site generator written in Python (based on the
popular [makesite.py](https://github.com/sunainapai/makesite) project), and all
the layout/content files for my peronal website (above). Feel free to test it
out and modify it to fit your needs.

### I. Directory Structure

Below I describe the directory structure of this project.

**_It is IMPORTANT this directory structure is maintained for all content,
layouts, and style/script files or the `makesite.py` script will not process
them correctly._**

#### A. content/

The `content/` directory contains five separate sub-directories: one to hold the
content that is displayed on each page of the (generated) website (i.e.,
_index.html_, _experience.html_, _publications.html_, and _research.html_), and
one that stores content shared across pages (e.g., lists of links to media
related to different projects I've worked on).

**There are a few things to note about content files and how they are
organized:**

1. **Mardown** and **HTML** are currently the only supported content file
   formats.

2. **Content files that are nested within sub-directories of the page-specific
   content directories** (e.g., `experience/past_jobs/*`) are interpretted as
   **listable** content by the `makesite.py` script. For example, each content
   file in `experience/past_jobs/` will fill a matching _list item_ layout
   template defined in `layout/list_items/` (i.e.,
   `layout/list_items/past_jobs.html`). Then, all processed list items will be
   combined into a single list element to fill a matching tag in the final
   layout, i.e., the _{{ past_jobs }}_ tag in `layout/pages/experience.html`.

3. **Content files that are placed directly under the corresponding
   page-specific content directories are NOT listable**, and will fill a
   matching tag directly in the corresponding page layout in `layout/pages/`.
   For example, the `content/index/bio.md` content file will fill the
   _{{ bio }}_ tag in `layout/pages/index.html`. _One exception to this rule is
   the the content files in `content/publications/*` which are listable, since
   they are told to be listable in the `makesite.py:320` script._

#### B. layout/

The `layout/` directory contains three separate sub-directories that contain
HTML layouts of the various site pages and page elements.

1. `layout/base/`: contains two base layouts that define the navigation bar
   (`nav.html`) and general structure of each website page (`page.html`). The
   navigation layout gets injected into the page layout, and the page layout
   gets injected with different page-specific layouts to form the final website
   pages.

2. `layout/list_items/`: contains several list item layouts for various list
   (\<ul\>\</ul\>) elements embedded in each page. These layouts get injected
   with content that is nested within sub-directories of the page-sepific
   content directories (Section I.A.2).

3. `layout/pages/`: contains a layout for each page in the final website. These
   layouts get injected with content from the page-specific content directories
   (Section I.A).

#### C. static/

The `static/` directory contains static styling, scripts, images, documents
(e.g., my CV), and publication manuscripts/slides.

#### D. third_party/

The `third_party` directory contains third party styling and scripts used to
construct this website. All third party files are accompanied with lincense
headers that dictate their terms of use.

### II. Generating/Testing the Site Locally

Follow these steps to generate and serve the website locally (at
localhost:8000):

1. fork this repository
2. `cd mywebsite`
3. create a Python `virtualenv` for this project
4. install all Python dependencies in the `virtualenv` with
   `pip install -r requirements.txt`
5. `make test`

### IV. Installing _Prettier_ Autoformatter for Development

I use [Prettier] as an autoformatter for all things web-related
(HTML/Markdown/CSS/JavaScript). It keeps things tidy and is easy to install with
the Node Package Manager (`npm`) that can be installed
[here](https://www.npmjs.com/get-npm). Once `npm` is installed, and you fork
this repository, you can install prettier simply with:

`npm install`

### V. Modifying Layouts/Content

To modify this site to suit your needs:

1. Fork this repository.
2. See below for example modifications.

#### A. Tailoring the Site with My Information

1. Open the `params.hjson` file.
2. Edit contents with your information.

#### B. Adding a Publication

1. Copy an example content file in `publications/`.
2. Edit the date in the name of the file (this is used to order them by date).
3. Edit the contents of the file.
4. If you have links to other content related to this publication, e.g. videos,
   slides, etc., add a content file with only these links in `content/shared/`
   directory (see existing examples), so these links can be used on other pages
   too.

#### C. Adding News Item

Follow steps 1-3 in above (_Adding a Publication_), but see example content in
`content/index/news/`.

#### D. Adding a Past Job Item

Follow steps 1-3 in above (_Adding a Publication_), but see example content in
`content/experience/past_jobs/`.

#### E. Creating an Additional Page

1. Read Section I.A (above) thoroughly.
2. Create a new HTML page layout file in `layout/pages/`.
3. Add any page styling to `static/css/default.css`.
4. Add any scripting to `static/css/custom.js`.
5. Create a matching content directory in `content/<name of page>/`.
6. Fill content directory created above with content files that match tags in
   the page layout.

#### F. Adding Listable Content to a Page

1. Read Section I.A (above) thoroughly.
2. Create a new list item layout file in `layout/list_items/` that has a tag for
   where the list will be injected.
3. Add any list styling to `static/css/default.css`.
4. Add any scripting to `static/css/custom.js`.
5. Create a matching listable content directory in
   `content/<name of page>/<item list tag>/`. **It is important this directory
   name matches the tag in the page layout where the list will be injected.**
6. Fill content directory created above with content files that will fill list
   items.

# Deploying to AWS

I use [AWS Amplify](https://aws.amazon.com/amplify/) for hosting and continious
deployment of my site. It costs only \$1.50/mo (at the time of writing), and is
both simple and reliable. Configuring the deployment is so easy, I messed up the
configuration during my first two attempts because I thought it required more
button clicking than necessary.

To avoid my mistakes, and deploy this site to AWS Amplify:

1. Make an AWS account.
2. Log in to the AWS console.
3. Register a domain for your site. I use **AWS Route 53** (search for it in the
   console).
4. Search for **AWS Amplify** in the console.
5. Click "New app"->"Host web app"
6. Select _GitHub_ as location of source code.
7. Authorize AWS to access your GitHub repositories.
8. Select your GitHub that contains your app, and click "Next"
9. Upload the build configuration (`amplify.yml`) contained in this repository.
10. Wait for it to provision resources and build the site.
11. Verify the site looks like it did when you tested it locally.
12. Click "Connect a Domain" and follow the instructions.

Now, anytime you push a commit to your fork of this GitHub repository, AWS
Amplify will pull down the changes and automatically deploy them to your site!
