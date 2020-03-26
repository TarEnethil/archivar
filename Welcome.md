# Welcome to Archivar!

Thank you for trying out this Archivar.
This is the welcome / home page, where every user will land after login.

## First things first: admin stuff

The following is a list of things you can / should do before you let the users login for the first time.

* Check config.py for settings like max media file size and CDN toggle
* Check the general settings for things like the page title and this welcome message
* Set up the map (see below)
* Set up the calendar (see below)
* Check the default settings for the modules such as default visibility for new wiki articles, events, locations and media
* Create users (they will be forced to change their password after the first login) with their respective roles

### Map setup

The map must be provided in the XYZ-Tile format.
There are several tiling programs out there which will cut up a large map image into multiple chunks and zoom levels.
These need to be placed into the data/map/ directory (or a subdirectory) and the tiling-format-string must be provided in the map settings.
You can also use an external provider (such as an apache server), as I am not sure if the performance of a flask is sufficient.
If you didn't install the basic location types, then you will need to add some manually before the first location can be created.

### Calendar setup

To set up the calendar, you will need to define epochs (or ages), months and days of your world.
After some constraint checking, the calendar needs to be finalized before events can be added to it.


## Roles

Users can have different roles, which mainly affect visibility of hidden / not yet approved content and access to settings.

### Admin / DM
This is the highest role.
It can see and access all content.
An admin can't revoke its own admin role, but can remove the role from other admins.
The admin account created at setup is an exception to this, as this account can't be stripped of its admin status.
Admins are the only one who can see the fields denoted with "DM notes" or similar annotations.

### Map admin
Map admins can change the map settings and add new location types.
They can also see hidden locations created by normal users or other map admins.
Hidden locations created by an admin can't be seen by map admins.
This role was introduced to have some trusted people help with the world building aspect without giving away all GM secrets.

### Wiki admin
Wiki admins can change the visibility of wiki articles created by users or other wiki admins as well as edit the wiki settings.
As with the map, hidden articles by admins are not visible to this role.
They dont see the hidden GM notes on articles.
This role allows for someone to help with the worldbuilding without giving away all GM secrets.

### Event admin
As with Map and Wiki admins, this role can toggle the visibility of articles created by users and other event admins, but not the ones created by admins.
This role is intended as a curator for the history of the world.

### Media admin
By now, you can guess what a media admin can do.

### Special
_Reserved. No function as of yet._


## Modules

There are several modules which are loosely linked.
For world building, the important ones are the Map, the Wiki and the Calendar.

### Main page, Navbar, Editor

The main page is the landing page after login.
The content can be controlled in the general settings.
You can also define quicklinks in the general settings, which will be display in the top navbar.

Many forms will have a markdown editor for rich text formatting.
The red star icon will bring up a sidebar with a filterable list of all visible entities from Characters, Events, Parties, Sessions and the Wiki, which allows for quick crosslinking between those modules.

### Characters and parties

Users can create their own characters, which can be grouped into parties.
A character can be part of multiple parties.

### Session

You can plan your next playing sessions (with multiple different campaigns!).
Characters or parties can be assigned to be part of the session.

### Map

Users can place locations on the map with a small description and a link to a wiki page (for more info).
The map also has a filterable list of all visible locations.

### Wiki

Players can create wiki articles to give more information about entities in the world like gods, cities and great heroes.
Articles can have tags and a category to group them (no category nesting supported).

### Calendar

After the calendar is finalized by an admin, users can create new events to fill the history of the world with life.

### Media

Users can upload files here, which can be referenced in with the markdown editor sidebar.

## In case of bugs

If you run into any problems, you can contact me via:

* [Github profile](https://github.com/tarenethil)
* [Link to this project](https://github.com/tarenethil/archivar)
* [reddit](https://old.reddit.com/u/tarenethil)