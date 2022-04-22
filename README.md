# Archivar, a collaborative world building tool
Hi!
While DMing for my D&D group, I wanted a possibility for us to collaboratively build the world together.
As my (not thorough) search came up with nothing, I decided to build something myself.
The following readme gives an introduction into what this project is (or isn't), how to install/use it and what it is built upon.

**TL;DR**: This is a web-based, game engine agnostic tool for collaborative world building and campaign / session management for role playing groups.
It is using Flask with SQLite as a backend with a bootstrap-powered frontend.

# Installation
For ways to install and run Archivar, see [INSTALL.md](INSTALL.md).

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
* A place to keep track of your character's stats (use roll20 or a piece of paper for that)

# Features
## Users
Users can only be created by an admin, so the admin has to tell the user his username and password.
After the first login (or any login after an admin changed the password), the user will need to change his password.
Passwords are stored hashed and salted.

### Characters and Parties
Each user can create multiple characters, which only have very basic attributes as to be game engine independent.
An admin may group characters into a party, which currently only serves the purpose of an easier picking of characters for recurring sessions and to share information between party members.
A character can be in multiple parties at once.

## Campaigns and Sessions
An admin can create campaigns and can assign a user as the DM.
The DM can schedule sessions for the campaign and select which characters will participate.
Besides a public summary, sessions also have a hidden notes section only visible to DMs.
When viewing the session list, characters of the viewing user are highlighted.

## Wiki
The wiki is one of the three major world building tools.
It can store information about npcs, items, places and many other things.

## Map
The original inspiration for building this collaboration tool and the second of the big three.
An admin can create one or multiple maps, that can be linked / nested within each other.
Every user can add locations and descriptions to the maps, with customizable icon sets.

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
* Frontend with [Bootstrap 5.1.3](https://getbootstrap.com/docs/5.1/) and [Bootstrap Dark](https://vinorodrigues.github.io/bootstrap-dark-5/)
* JavaScript framework is [jQuery](https://jquery.com/), additional scripts:
    * [multiselect](http://loudev.com/): select characters for session and parties
    * [bootstrap-select](https://developer.snapappointments.com/bootstrap-select/): filtering in selects
    * [quicksearch](https://deuxhuithuit.github.io/quicksearch/): filtering in multiselects
    * [tempus dominus](https://github.com/tempusdominus/bootstrap-4): date time picker
* Map built with [leaflet.js](https://leafletjs.com/)
* Markdown done with [easyMDE](https://easymde.tk/) (WYSIWYG editor) and Flask-Misaka (on-server rendering)
* Thanks to the [Flask Mega Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) by Miguel Grinberg for getting me started with Flask
