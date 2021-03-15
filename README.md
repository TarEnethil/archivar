# Archivar, a collaborative world building tool
Hi!
While DMing for my D&D group, I wanted a possibility for us to collaboratively build the world together.
As my (not thorough) search came up with nothing, I decided to build something myself.
The following readme gives an introduction into what this project is (or isn't), how to install/use it and what it is built upon.

**TL;DR**: This is a web-based, game engine agnostic tool for collaborative world building and campaign / session management for role playing groups.
It is using Flask with SQLite as a backend with a bootstrap-powered frontend.

# Installation
Until now, I only did this on linux.
Because the use of virtual environments, it should be no big deal to use this on Windows too.

## Set up python virtual environment
Flask apps are usually run inside python virtual environments, which allows the installation of dependencies without needing global permissions.
You can either set them up with python or python3.

### python
```bash
virtualenv venv
```

### python3
```bash
python3 -m venv venv
```

### enter venv and install dependencies
```bash
. venv/bin/activate
pip install -r requirements.txt
```

If the installation of Pillow gives you troubles, you might need to install the packages libjpeg8-dev, zlib1g-dev and python-dev (or python3-dev).

## Initial configuration and database init
```bash
flask db upgrade
```

The script will run flask db init and flask db upgrade, while providing the migration-files from this repository (allowing for incremental database structure changes).

## Local run (or deploy on a server)
```bash
export FLASK_APP=dmcp.py
flask run -h localhost
```

## Creating admin account
* Visit http://localhost:5000/__install__ to be guided through installation
* Installation also includes some default settings if wanted
* After installation, log in with the admin account and head to the (module) settings

# Deployment
I nanaged to deploy this with apache, please refer to other tutorials on how to deploy a flask application on a real server.

# What this is
Archivar is a web-based tool for collaborative world building, as well as campaign management for role playing groups.
It is intended to be used with a small to semi-large group of people who trust each other and are interested in filling their world with places, information and stories.
Archivar allows for people to collaborate on places in the world (map), knowledge about the world (wiki) and timelines within the world (calendar, tbd).
Users can create their own engine-agnostic characters and add information and stories about them as well.
For DMs, this tool allows for keeping track of all the information of the world, as well as DM-specific tidbits that are hidden from other users.
Besides the world building, it can be used to plan/announce play sessions for one or more campaigns within the world.

Archivar was started and is fully intended to be a private project.
This means that functionality or design may change at any time if I see it fit.
It is a work in progress and probably will be for a long time.
Only by using it will I be able to hone the experience (and also tailor it a bit towards my use cases).

# What this isn't
* The best way of doing stuff (there are better map tools, session planers or wikis out there, but this place bundles the functionality I like to have in one place)
* Pretty (The design is pretty bare bones, at the moments it is function over design for me)
* A replacement for roll20 (it is a an addition at best)
* A place to keep track of your characters' stats (use roll20 or a piece of paper for that)

# Modules
## User
Users can only be created by an admin, so the admin has to tell the user his username and password.
After the first login (or any login after an admin changed the password), the user will need to change his password.
Passwords are stored hashed and salted.

### Characters and Parties
Each user can create one or more characters, which only have very basic attributes as to be game engine independent.
Besides the public fields, a character has a field for comments which can only be seen by admins.
An admin may group characters into a party, which currently only serves the purpose of an easier picking of characters for recurring sessions.
A character can be in multiple parties at once.

## Session
An admin can schedule sessions for one or multiple campaigns.
To distinguish between different campaigns, use a different "code", which also brings the added benefit of automatic session numbering if wanted.
Besides a public summary, sessions also have a hidden notes section only visible to admins.
When viewing the session list, characters of the viewing user are highlighted.

## Wiki
The wiki is one of the three major world building tools.
It can store information about npcs, items, places and many other things.
Every user can add and edit articles, but if configured, they are hidden until curated by a (wik) admin.
Admins / DMs can also deliberately hide pages from non-admin users; these pages will not be included in search results or the navigation, but may still appear as links (although viewing acces will be denied to non-admins).
If the page was created by an admin (see Roles-section), wiki admins can't view/find/edit the page either.

## Map
The original inspiration for building this collaboration tool and the second of the big three.
Every user can add locations and descriptions to the world, with icons defined by (map) admins.
If configured, newly created locations are hidden until accepted by a (map) admin.
Hidden notes created by an admin are invisible to map admins as well.

### Map provider
The map currently only supports XYZ-maptiles.
The built-in map provider can be configured in the map settings, the map tiles have to be located somewhere within data/map/ with the correct xyz-String configured.
As this provider is possibly slow, you can also use an external provider such as nginx or apache.
I am currently looking for suitable tools for creating XYZ-maptiles from an image.

## Calendar and Events
Finishing of the three big features is a customizable calendar with events.
As admin you can create a calendar with customizable months, days and epochs.
Players can then enter events to define how the world was shaped.

## Media
Upload and categorize additional media like images (for wiki / character pages etc.) or additional documents like homebrew or house rules.

# Roles
The permission management is currently very simple.
There are only three roles: Admin, Moderator, User.
See [ROLES.md](ROLES.md) for information on who can do what.

# Used tools and libraries
* Backend is [Flask](http://flask.pocoo.org/) (Python), current Database is [SQLite](https://www.sqlite.org/index.html) (for used python libraries and flask extensions refer to requirements.txt)
* Frontend with [Bootstrap 4.4](https://getbootstrap.com/docs/4.4/)
* JavaScript framework is [jQuery](https://jquery.com/) (used by bootstrap), additional scripts:
    * [multiselect](http://loudev.com/): select characters for session and parties
    * [bootstrap-select](https://developer.snapappointments.com/bootstrap-select/): filtering in selects
    * [quicksearch](https://deuxhuithuit.github.io/quicksearch/): filtering in multiselects
    * [tempus dominus](https://github.com/tempusdominus/bootstrap-4): date time picker
* Map built with [leaflet.js](https://leafletjs.com/)
* Markdown done with [easyMDE](https://easymde.tk/) (WYSIWYG editor) and Flask-Misaka (on-server rendering)
* Thanks to the [Flask Mega Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) by Miguel Grinberg for getting me started with Flask
