Unvanquished support for DarkRadiant
====================================

Installation
------------

DarkRadiant is not yet usable for Unvanquished, but if you're a developer you can be interested by the game file for testing purpose.

Download the [game file](games/unvanquished.game) and put it in `install/games/` directory within darkadiant one.

Using
-----

Set the engine path in DarkRadiant preferences.

Keep in mind game directory must contain `pkg` directory (like `baseq3` was in Quake 3 dir).

Unvanquished has advanced file layout for maps and resources. Every map resides in separate .pk3.
Filename must obey the rule: `map-<mapname>_<mapversion>.pk3`, eg. `map-station_4.pk3`.

Unpacked files you are working with must be put into `map-<mapname>_<mapversion>.pk3dir` directory,
otherwise game will not find them.