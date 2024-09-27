# Changelog


## Version 0.6.2 (released 2024-09-27)

* Map: Fix icon in settings
* Use descending order for most queries
* Darkmode: Fix some issues in markdown editor
* Add last and next session to home page
* Fix new flake8 lints
* Docker: Switch to debian
* Dependencies: Bump everything and update to python 3.12
* Bump dependencies
* Map: fix sidebars
* Template: Bootstrap5 fixes
* Template: add basic user Themes
* Base: Add support for python3.10+
* Event: fix end date calculation error
* Template: add strikethrough button to markdown editor
* Map: use existing markdown render function
* Bump pillow from 8.3.2 to 9.0.1
* tmp: bootstrap-select hack
* BS5: patched bootstrap-select (jfc)
* Template: update to bootstrap 5.1.3
* User: fix password redirect
* Docker: speed up build
* Docker: Allow override of uid
* Calendar: fix markdown editor
* Base: add more validators
* Media: fix media.edit when not changing file
* Deps: Replace Flask-Bootstrap4 with Bootstrap-Flask
* Style: Harmonize validator names
* Tests: add missing validator tests
* Campaign: fix session creation link
* Event: fix sidebar loading
* Base: add version-suffix to local files
* Base: update bootstrap to 4.6.0
* Bump pillow from 8.1.1 to 8.3.2
* Template: Update fontawesome to 5.15.4
* Template: add 'More' dropdown
* Random: add rollable dice sets
* Add random endpoint and random tables
* Bump pillow from 8.2.0 to 8.3.2
* Bump pillow from 8.1.1 to 8.2.0
* Wiki: fix lightbox
* Campaign: improve timeline
* Map: fix wrong css include
* Journal: update journal.list style
* Campaign: add timeline
* Tests: run tests in CI
* Tests: add first unit test
* Refactor app.helpers
* ROLES.md: Update Party
* All: convert .format to f-strings
* Template: add image popups for markdown and profile pictures
* Workflows: prevent double workflow execution (#91)
* Devtools: add requirements.txt check to pre-commit-hook
* Debug: fix pyinfo (#90)
* Add linting with flake8, fix linter errors, add linting to CI (#89)
* Make archivar docker-ready


## Version 0.6.1 (released 2021-03-26)

Version 0.6.1 took some time due to a pause in development, but things should be back on track now.
Besides many bugfixes, the overhaul of the permission system is probably the biggest single change.
There are now only 3 roles: Admin, Moderator and User.
What each of these roles can do is documented in ROLES.md, although I am not satisfied with the role system yet.
Characters, Parties and Sessions now have a profile picture, we have some nicer prompt-Windows thanks to bootbox.js and DMs can now edit parties they DM for.

* Campaign: refactor javascript
* Template: use nicer confirm boxes
* Campaign: optionally add/del participants on party (de)select
* Multi: associate Parties with Campaigns
* Multi: only delete old profile pictures if present
* DB: fix migration with new Character model
* Base: also delete profile picture thumbnail
* Journal: add infobox where possible
* User: fix char visibility on profile
* Base: misc comments, code style
* Base: improve filename duplication avoidance
* Multi: don't reuse profile picture names
* MapNodeType: use refactored upload functions
* Media: use refactored upload functions
* Multi: Fail create/edit on failed image operation
* Base: refactor profile picture upload
* Forms: use correct FileField
* Campaign: fix profile picture upload
* Bump jinja2 from 2.10.1 to 2.11.3
* Campaign: add profile picture
* Character: add profile picture
* Bump pillow from 7.1.1 to 8.1.1
* Party: add profile picture
* Base: refactor filenames and thumbnail generation
* Docs: update README, add ROLES
* JS: Fix momentjs with datatable pagination
* Base: update datatables statics
* Session: fix date for session.edit
* Base: update momentjs
* Fix Session page for multi-campaign dms
* update requirements.txt
* Map: only use javascript log in debug mode
* Mixins: move is_viewable to SimplePermissionChecker
* Map: add number of locations to map list
* User: improve markdown-editor-height handling
* User: remove media sidebar settings
* Base: cleanups from role adjustments
* Map: adjust to new roles
* Wiki: adjust to new roles
* User: adjust to new roles
* Session: adjust to new roles
* Party: adjust to new roles
* Main: move page title from GeneralSettings to UserConfig
* Main: adjust to new roles
* Events: ajdust to new roles
* Journal: adjust to new roles
* Character: adjust to new roles + add visibility
* Campaign: adjust to new roles
* Calendar: adjust to new roles
* Media: more permission overhaul
* Sidebars: improve AsyncCategoryLoader
* Media: simplify permission handling
* Mixins: Add SimplePermissionChecker
* Base: simplify roles
* Devtools: add master-branch check to make_release.sh
* Media: fix file editing
* Media: only delete files if they exist
* Media: remove fake button from Template


## Version 0.6.0 (released 2020-05-13)

The main focus on this release was the upgrade from Bootstrap 3 to Bootstrap 4.
Beside that, the most notable change would be the new Media Sidebar, which is accessible from the markdown editor.
For it to be useful, image thumbnails are automatically created on upload.
The Media Sidebar is the base for all new sidebars and potentially some data pickers as advanced form elements in the future.
There were also some regressions from earlier works and bug fixes.

Detailed list of changes:

* Base: remove Flask-FontAwesome
* Base: prevent excessive database access on static files
* Media: prevent file extension change on edit
* Base: Fix upload file name duplication (again)
* Implement new Media Sidebar (#49)
* Template: improve flexbox markup
* Base: only use python3 format strings
* Config: rename config files for git tracking
* Devtools: add some debugging options
* Config: rename files for consistency
* Devtools: add debug config
* Template: Fix footer debug_mode detection
* Config: improve config handling
* Template: improve login on mobile
* Media: improve thumbnail handling
* Wiki: fix footer markup
* Devtools: add endpoint for debug info dump
* Base: add own markdown-classes to editor preview
* Base: fix editor fullscreen (again)
* Media: add asynchronous upload form to editor
* Media: add file count for category settings
* Media: add thumbnail-generation for images
* Base: Fix HTTP Error Handlers
* Wiki: fix eager navigation hover effect
* Devtools: add readme for DEV-mode
* Dev: re-add hints for dev-mode, rework footer
* Migrate from Bootstrap 3 to Bootstrap 4 (#44)
* Devtools: add README for dev tips
* Character: sort sessions by date
* Devtools: add venv check
* Template: fix editor fullscreen
* Devtools: add updating requirements to make_release
* Base: fix requirements
* Devtools: improve & add comments


## Version 0.5.1 (released 2020-04-25)

This release was mainly internal restructuring to make further development a little easier. Notable changes for users include:

* Switch markdown editor from SMDE to EMDE (active fork)
* Most URLs are now "pretty" (i.e. character-name is in the URL, still some TODOs for map & sidebars)
* List all sessions of a character
* Readd session numbering

Detailed list of changes:

* Devtools: add make_release.sh
* Convert changelog to Markdown
* Session: forgot to add migration file
* Session: add session number as db field
* Helpers: Fix imports
* Database: use render_as_batch for migrations
* Session: remove useless helper
* Base: fix db install step
* Template: close h2 if there are no past sessions
* Journal: use bootstrap-select for sessions
* Mixins: Fix param name
* Character: add Sessions table
* Init: cleanup code
* Base: Fix login_view url
* Models: rename SimpleAuditMixin -> SimpleChangeTracker
* Models: Port Mixins to own file
* Multi: split models into multiple files
* Test: split User from models.py
* Meta: overhaul application structure
* Template: fix some icons
* Replace simpleMDE by easyMDE
* Template: switch from glyphicon to fontawesome
* Template: add icon generator function
* Update Pillow
* Multi: remove unneeded imports
* Journal: add and use LinkGenerator
* Wiki: add and use LinkGenerator
* Map: add and use LinkGenerator
* User: add and use LinkGenerator
* Session: add and use LinkGenerator
* Party: add and use LinkGenerator
* Media: add and use LinkGenerator
* Event: add and use LinkGenerator
* Campaign: add and use LinkGenerator
* Calendar: add and use LinkGenerator
* Character: add and use LinkGenerator
* Add LinkGenerator class
* Requirements: fix python 3.8 install
* Session: improve session creation for multi campaign dms
* Wiki: Prevent Main Page from being renamed
* Map: redirect .index to .view for pretty URL
* Template: add configuratble dataTable threshold
* Calendar: add number of events to category list
* Campaign: fix button label
* Map: implement pretty URLs
* Journal: implement pretty URLs
* Wiki: implement pretty URLs
* Session: implement pretty URLs
* Party: implement pretty URLs
* Media: implement pretty URLs
* Event: implement pretty URLs
* Campaign: implement pretty URLs
* Calendar: implement pretty URLs
* Character: implement pretty URLs
* Base: add urlfriendly filter
* Session: Fix missing border-color


## 0.5.0

* Character: Add missing css include
* Template: prevent SMDE from after-loading from CDN
* Template: Add missing file for multi-select
* Session: (Forms) Add player name to participant lists
* Multi: Unify page_title Capitalization
* Multi: Unify Button Capitalization
* Multi: rename Map Node (Types) to Location (types)
* Multi: unify submit button label Capitalization
* Template: unify Heading Capitalization
* Template: render flash() with bootstrap utils
* User: add campaigns to user.profile
* Base: add campaigns to statistics
* Campaign: add icon, add info to .view
* Sessions: Link sessions and campaigns
* Meta: add campaigns (first steps)
* Merge pull request #2 from TarEnethil/dependabot/pip/validators-0.12.6
* Merge pull request #1 from TarEnethil/dependabot/pip/pillow-6.2.0
* Multi: update more page titles
* Character: add proper party table
* Multi: add quantifiers to table headings
* Map: show no table if there are no node types
* Character: fix journal query
* dependabot[bot] Bump validators from 0.12.4 to 0.12.6 (origin/dependabot/pip/validators-0.12.6)
* dependabot[bot] Bump pillow from 3.3.2 to 6.2.0 (origin/dependabot/pip/pillow-6.2.0)
* update requirements.txt (CVE-2019-14806)
* Session: add follow-up session creation
* User: add date formats with weekdays
* Dev: add style for dev environment
* General: Improve &lt;title&gt;


## 0.4.5

* Template: hide empty quicklink menu
* install: fix installation with new db-init script
* Wiki: add datalist for categories
* Session: add datalist for campaign codes
* Sessions: sort session participants by name
* Sidebar: fix use_embedded_images option
* User: add quicklink option
* Template: improve global quicklink handling
* Template: remove width of login page
* Character: Fix journal creation
* Template: Add h5/h6 style for markdown
* Event: add create link on event.list (context sensitive)
* Media: add create link on media.list (cat sensitive)
* Template: add quicklinks for some settings
* Template: add subheading padding for markdown
* Editor: add map node sidebar
* Template: Fix SMDE-JS error for non-admins
* Sidebar: don't show empty categories on media sidebar
* User: consolidate phb-style options
* Session: add quicklinks for journal create/edit


## 0.4.4

* Statistics: make dict ordered, add missing statistics
* Forms: customize submit button label per form
* Session: add relevant journals to session.view
* Character: add character journals
* Wiki: add category renaming in settings
* Forms: add better redirects after create/edit
* User: add options for default media sidebar checkboxes
* Session: change next session button arrow location
* Requirements: Update SQLAlchemy due to 2 CVEs
* Template: reduce footer width
* Template: add new footer-func of auditMixin to pages
* db: add auditMixin to general settings
* Database: add SimpleAuditMixin
* Template: Fix markdown rendering in some templates


## 0.4.3

* Hotfix2 (added later):
    * Requirements: Fix jinja version (was reverted erroneously)
* Hotfix (added later):
    * Requirements: Update Pillow due to CVE-2016-9189
    * Requirements: add requirements for Flask-Misaka
* (Experimental): Switch to on-server markdown rendering
* Template: show footer on all pages*
* All: add @decorators for access control
* Base: change priority of base url
* Session: allow session members to edit sessions
* Party: allow party members to edit party
* Template: add new-char link to character table
* requirements: increase Jinja2 version due to CVE-2019-10906
* Template: move delete buttons to the right
* User: add editor_height option
* Map: fix editor height for map forms
* Map: add node permalinks to popups
* Char/Party: Reverse order of tables
* Char/Party: Fix inpage navigation
* (hotfixed earlier) Base: fix editor sidebars


## 0.4.2

* Readme: add installation info
* Template: simplify admin nav bar
* Template: Clean up js helpers
* Template: harmonize js helper includes
* Character: add character deletion
* Party: add party deletion
* Session: add session deletion
* Wiki: add article deletion
* Event: add event deletion
* Event: Fix event edit page
* Char: change redirect after character edit
* Calendar: redirect admin on non-finalized calendar
* Template: Set height for markdown editor


## 0.4.1

* Base: add changelog and statistics pages
* User: Fix conditional data table on profile


## 0.4.0 'M-M-M-Multi-Map'

* Merge multi-map into master: add multi map support
* Map: remove unused import
* Map: Rename endpoints for clarity
* User: add conditional data table for characters
* Calendar: Format moon title attrs
* Map: add default_map setting
* Map: display map name in topright corner
* Map: improve wiki and submap links
* Map: implement submap linking for map nodes (admin)
* Map: implement map visibility option
* Map: implement multiple map operations
* Map: make nodes belong to one map only
* Map: add view endpoint for multi maps
* Map: add settings editing for multiple maps
* Map: add map.create for first map
* Map: Split MapSettings table
* Party/Session: refactor multi-select filtering
* Multi: add comments to helpers
* Doc: update readme and welcome message


## 0.3.4

* Template: add quicksearch feature for multi-select
* Map: make map check interval configurable
* Map: add warning if map was edited by someone else
* Character: make character and party list public
* Template: Fix two js include paths
* Media: Fix typo in settings
* Characters: Add datatables to char/party list
* Calendar/Event: improve moon title


## 0.3.3 'Luna'

* Models: replace xrange with range
* Calendar/Event: add moon colors
* Calendar/Event: even better moon display
* Base: Fix flask_bootstrap local CDN serve (weird)
* Calendar: add moon phase naming
* Calendar: improved moon display formula
* Calendar/Event: Add moon phase calculation
* Event: Fix css import
* Config: sort and add comments
* Templates: Fix various javascript errors
* Template: Fix editor sidebar with multiple editors
* Character: add private_notes field
* Template: Change CDN-usage settings handling
* DB: Fix migrations
* User: make roles visible on profile (to anyone)
* Calendar: add moons
* Settings: Add option to use CDN for scripts


## 0.3.2

* Wiki: fix str encoding error
* Event: add datatable for events
* Style: Restrict image width in markdown renderings
* Readme: add Media endpoint description
* Media: add media deletion
* Multi: add dataTables where necessary
* Media: add max filesize to upload page
* Wiki: Fix wiki dropdown, remove not needed helper


## 0.3.1

* Media: Fix visibility checkbox on media form
* Wiki: Fix sidebars
* Media: add custom 413 page
* Base: Fix setup


## 0.3.0

* Event: Fix event.view user links
* Map: Fix dropdown heights in map forms
* Event: Fix event.view permissions
* Media: Add Media blueprint
* Media: Add Media sidebar


## 0.2.2

* Admin: add last-seen to userlist
* Base: new password must differ from old password if force_pw is active
* Base: hide quicklinks for non-authed users
* Base: make topnav sticky
* Base: fix editor-sidebar and location-list height
* Base: add collapsible topnav for mobile users
* Base: clicking the red star icon again closes editor-sidebar
* Wiki: add article heading to markdown window (h1)
* Event: Fix event category dropdown height on Windows


## 0.2.1

* Event: Fix HTTP500 at event creation
* Base: Use dedicated password-change form for forced password 
