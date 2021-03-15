# Calendar
## Epochs, Months, Days, Moons
### Calendar not finalized
* Add: Admin
* Edit: Admin
* Hide: not hideable
* Delete: Admin

### Calendar finalized
* Add: Nobody
* Edit: Moderator (Name / Description only)
* Hide: not hideable
* Delete: not deletable

# Campaign
* Add: Admin
* Edit: Admin, DM (own Campaign only)
* Hide: not hideable
* Delete: not deletable

# Character
* Add: User
* Edit: Owner
* Hide: Owner
* Delete: Owner, Admin (if visible)

Note: Characters can only be selected as Party Members / Session Participants if they are visible.
Should they be hidden after being added to a Party or Session, their name is still visible, although their Character-page will not be accessible for other users.

# Journal
* Add: Character-Owner
* Edit: Owner
* Hide: Owner
* Delete: Owner, Admin (if visible)

# Event
* Add: User
* Edit: Owner, User (if visible)
* Hide: Owner
* Delete: Owner, Moderator (if visible)

## Event Settings
* Edit: Moderator

## Event Category
* Add: Moderator
* Edit: Moderator
* Delete: not deletable

# Main
## General Settings
* Edit: Moderator

# Map
* Add: Admin
* Edit: Admin
* Hide: Admin
* Delete: not deletable (TODO?)

## Map Settings
* Edit: Moderator

## Location
* Add: Owner (of Map), User (if Map visible)
* Edit: Owner (if Map visible), User (if visible and Map visible)
* Hide: Owner, Moderator (if visible and Map visible)
* Delete: Owner, Moderator (if visible and Map visible)

## Location Type
* Add: Moderator
* Edit: Moderator
* Hide: not hideable
* Delete: not deletable

# Media
## Media Item:
* Add: User
* Edit: Owner, Moderator (if visible)
* Hide: Owner
* Delete: Owner, Moderator (if visible)

Note: even if hidden, direct links to media items (including pictures and thumbnails) will still work / be displayed.
this is so that they can be served as static files by the wsgi parent.
Link with caution!

## Media Settings:
* Edit: Moderator

## Media Category:
* Add: Moderator
* Edit: Moderator
* Delete: not deletable

# Party
* Add: Admin
* Edit: Admin, User (when Character in Party)
* Hide: not hideable
* Delete: Admin

# Session
* Add: Admin, User (when GM of Campaign)
* Edit: Admin, User (when GM of Campaign or Character in Session)
* Hide: not hideable
* Delete: Admin, User (when GM of Campaign)

# User
* Add: Admin
* Edit: Admin, User (Self only)
* Hide: not hideable
* Delete: not deletable

# Wiki
* Add: User
* Edit: Owner, User (if visible)
* Hide: Owner
* Delete: Owner, Moderator (if visible)

## Wiki Settings
* Edit: Moderator