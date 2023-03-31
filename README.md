# DeadBot

This bot helps companies and teams keep track of project deadlines by automatically sending reminders to specified roles before the deadline. It also updates the remaining days until the deadline daily.

## Features

- Create deadlines with a project name, description, deadline date and time, timezone, and team roles.
- Automatically send reminders to specified roles at 10, 5, and 2 days before the deadline.
- Update the remaining days until the deadline in the deadlines channel daily.

## Setup

1. Install the required Python packages by running: `pip install -r requirements.txt`
2. Replace the `TOKEN` variable in the code with your bot's token.
3. Run the bot script using Python 3.9 or later.

## Usage

To create a deadline, use the `/deadbot` slash command followed by the options:

- `project_name`: The name of the project. (Required)
- `description`: A description of the project. (Required)
- `deadline_date`: The deadline date in YYYY-MM-DD format. (Required)
- `deadline_time`: The deadline time in HH:mm format. (Required)
- `timezone`: The timezone abbreviation (e.g., HKT). (Required)
- `roles`: The roles to be notified, separated by commas. (Required)

Example:

/deadbot project_name="Project Alpha" description="Complete the first phase of Project Alpha" deadline_date="2023-04-30" deadline_time="23:59" timezone="HKT" roles="@TeamAlpha, @TeamBeta"


This command will create a deadline for "Project Alpha" and notify the "Team Alpha" and "Team Beta" roles.

## Deadlines Channel

The bot will automatically create a `#deadlines` channel in the Discord server, where all the deadlines will be posted and updated daily with the remaining days until the deadline. The channel is accessible only to the bot and server administrators.

## Background Tasks

The bot runs two background tasks:

1. `update_deadlines_task`: Updates the remaining days until the deadline in the deadlines channel daily.
2. `send_reminders_task`: Sends reminder messages to the specified roles at 10, 5, and 2 days before the deadline.

## Notes

- The bot only supports timezone abbreviations.
- Deleting a deadline message from the `#deadlines` channel will remove the deadline from the bot's memory.
