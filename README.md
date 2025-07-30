# qwacker

Utility Discord bot designed for the CSC Duclings server, primarily used for housekeeping tasks at the beginning and end of each semester.

## Running

First, configure the `.env` file with the required environment variables:

```dotenv
DISCORD_BOT_TOKEN=abcdefg
GUILD_ID=1234567
```

Install the necessary dependencies:

```shell
uv sync
```

Run the bot using the following command:

```shell
uv run task start
```

## Commands

### Channel Archival

The archival command moves specified channel(s) to a different category and sets them to read-only.

```
/archive to_archive destination [suffix]
```

- `to_archive` — The text channel or category to be archived.
- `destination` — The category to which the text channels will be moved.
  - Note: The category should be configured as read-only, but the bot does not enforce this; it will inherit the permissions of the parent category.
- `suffix` (optional) — An optional suffix to add to channel names.

### Discussion Leader Setup

This command creates `@Team DL` roles and `#❓ask-channels` for Discussion Leaders.

> [!NOTE]
> The bot does not handle role assignments; this is managed by [Carl-bot](https://carl.gg). After executing the command, use Carl-bot's `/reactionrole` feature to enable role assignments.

```
/dl setup category role_channel csv_file
```

- `category` — The category where the `#❓ask-name` channels will be created.
- `role_channel` — The channel in which the role assignment embed will be posted.
  - Note: This channel should be set as read-only, although the bot does not enforce this.
- `csv_file` — A CSV file formatted as described below.

#### CSV format

The uploaded CSV file must have column headers in the first row, which are **case-sensitive**.

**Required fields:** These fields must be present, and each row must have corresponding values.

- `First` — First name of the Discussion Leader.
- `Last` — Last name of the Discussion Leader.
- `Email` — Email address of the Discussion Leader.
- `Sections` — Sections assigned to the Discussion Leader (must be a comma-separated string of integers, e.g., `"45, 22"`).

**Optional, but really-should-have fields:** These fields are not mandatory but are highly recommended. If included, not all rows need to have values.

- `Preferred` — The preferred name of the Discussion Leader.
  - If provided, this name will be used for the channel and role; otherwise, the first name will be used.
- ~~`Username` — The Discussion Leader's Discord username (used for automatic role assignment).~~
- `Emojis` — A string of emojis chosen by the Discussion Leader; the first available choice will be used for role assignment. If empty, a random emoji will be assigned.
- `Timestamp` — An ISO 8601 timestamp (e.g., `2024-08-27T08:47:04`). The timestamp helps determine priority for emoji selection.

Any other columns will be ignored.

**Example CSV Formats**

**With Required Fields Only:**

| First  | Last  | Email           | Sections |
|--------|-------|-----------------|----------|
| Donald | Duck  | dduck@sfsu.edu  | 12, 34   |
| Minnie | Mouse | mmouse@sfsu.edu | 55, 78   |

**With All Fields (Including an Ignored "ID" Field):**

The `ID` field will be ignored by the bot but may be useful for identifying Discussion Leaders if form responses are being collected.

In this example:
- Donald Duck’s role and channel will be `@Team Duc` and `#❓ask-duc` because a preferred name is provided.
- Minnie’s role and channel will be `@Team Minnie` and `#❓ask-minnie`.
- Minnie will receive the 🐭 emoji, while Mickey will receive 🧀 as their second choice due to a later timestamp.

| First  | Last  | ID        | Email            | Sections | Preferred | Username  | Emojis   | Timestamp           |
|--------|-------|-----------|------------------|----------|-----------|-----------|----------|---------------------|
| Donald | Duck  | 999999991 | dduck@sfsu.edu   | 12,34    | Duc       | qwackling | 🐥🎉⚾️   | 2024-08-09T09:59:04 |
| Minnie | Mouse | 999999992 | mmouse@sfsu.edu  | 55, 78   |           | jerry     | 🐭🚃🍌📮 | 2024-08-10T14:37:05 |
| Mickey | Mouse | 999999993 | mmouse1@sfsu.edu | 15, 49   |           | jinx      | 🐭🧀     | 2024-08-12T14:37:05 |

### Rules

Use these commands to post or update server rules. The content of the rules embed is hardcoded in the source code.

> [!IMPORTANT]
> Ensure that Carl-bot is configured to assign the `Member` role to users who react to the posted rules message.

```
/rules post [destination]
/rules update channel message_id
```
