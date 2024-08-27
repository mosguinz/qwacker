# qwacker

Utility Discord bot for CSC Duclings server. It is meant for housekeeping purposes at the start and end of each
semester.

## Run

First, populate the `.env` file:

```dotenv
DISCORD_BOT_TOKEN=abcdefg
GUILD_ID=1234567
```

Install dependencies:

```shell
poetry update
```

Then run it:

```shell
poetry run python -m bot
```

## Commands

### Channel archival

"Archive" channel(s) by moving them to a different category and making them read-only.

```
/archive to_archive destination [suffix]
```

* `to_archive` -- Text channel or category to archive.
* `destination` -- Category to move the text channels to.
    * This category's permission should be read-only. The bot does not enforce this. It will inherit the permissions of
      the parent.
* `suffix` (optional) -- Suffix to add to channel names.

### Discussion Leader setup

Creates `@Team DL` and `#❓ask-channels` for Discussion Leaders.

> [!NOTE]
> The bot does not handle role assignments. [Carl-bot](https://carl.gg) does. After running the command, you
> will need to use Carl-bot's `/reactionrole` feature to enable role assignments.

```
/dl setup category role_channel csv_file
```

* `category` -- Category to create the `#❓ask-name` channels.
* `role_channel` -- The channel to post the role assignment embed.
    * This channel should be read-only. The bot does not enforce this.
* `csv_file` -- A CSV file in the format described below.

#### CSV file format

The first row of the uploaded CSV file must be column headers. Column headers are **case-sensitive**.

##### Required fields

* `First` -- The Discussion Leader's first name.
* `Last` -- The Discussion Leader's last name.
* `Email` -- The Discussion Leader's email.
* `Sections` -- Sections belonging to the Discussion Leader.
    * This must be a comma-separated string of integers e.g., `"45, 22"`.

##### Optional, but *really-should-have* fields

* `Preferred` -- The Discussion Leader's preferred name.
    * If provided, this will be name used for their channel and role. Otherwise, their first name will be used.
* ~~`Username` -- The Discussion Leader's Discord username. This is for automatic role assignment.~~
* `Emojis` -- A string of emojis chosen by the Discussion Leader. The first available choice will be used for role
  assignment. If empty, a random emoji will be chosen.
* `Timestamp` -- An ISO 8601 timestamp e.g. `2024-08-27T08:47:04`. Offset is optional. This is used to determine the
  priority given for emoji preference.

Other columns will be ignored.

##### Examples

**Required fields only**

| First  | Last  | Email           | Sections |
|--------|-------|-----------------|----------|
| Donald | Duck  | dduck@sfsu.edu  | 12, 34   |
| Minnie | Mouse | mmouse@sfsu.edu | 55, 78   |

**All fields, including an "ID" field**

The ID field is ignored by the bot, but you may have it to identify the Discussion Leader if you are collecting form
responses.

Here:
* Donald Duck's team role and channel name will be: `@Team Duc` and `#❓ask-duc` because a preferred name is
  provided.
* Minnie's however, will just be `@Team Minnie` and `#❓ask-minnie`.
* Minnie will get 🐧 for their role, while Goofy will get their second choice, 🐶, because their timestamp is after
  Minnie's.

| First  | Last  | ID        | Email           | Sections | Preferred | Username  | Emojis   | Timestamp           |
|--------|-------|-----------|-----------------|----------|-----------|-----------|----------|---------------------|
| Donald | Duck  | 999999991 | dduck@sfsu.edu  | 12,34    | Duc       | qwackling | 🐥🎉⚾️   | 2024-08-09T09:59:04 |
| Minnie | Mouse | 999999992 | mmouse@sfsu.edu | 55, 78   |           | jerry     | 🐧🚃🍌📮 | 2024-08-10T14:37:05 |
| Goofy  | Dog   | 999999993 | gdog@sfsu.edu   | 15, 49   |           |           | 🐧🐶     | 2024-08-12T14:37:05 |

### Rules

Post or update the rules. The embed is hardcoded in the source.

> [!IMPORTANT]
> Make sure that Carl-bot is set up to assign the `Member` role for users reacting to this message.

```
/rules post [destination]
/rules update channel message_id
```
