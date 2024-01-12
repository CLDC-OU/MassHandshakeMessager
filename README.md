# MassHandshakeMessager

Automate Career Services sending mass messages to students on [Handshake](https://joinhandshake.com/)

## Setup

1. Ensure all [Dependencies](#dependencies) have been installed
2. Setup [Configuration](#configuration)

## Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### students.csv

This is the list of students to send the message to. Only the students Handshake ID is required to be in the csv. Other columns are optional.

> [!IMPORTANT]
>
> Be sure to use the Handshake ID, NOT the student's card id. The Handshake ID is the number in the url when viewing a student's profile. For example: `https://app.joinhandshake.com/users/12345678` has a Handshake ID of `12345678`.

### config.json

Create a file in the root of the project directory called `config.json` and set up the following properties

- `student_csv_filepath` (string): The filepath to the student csv. Can be an absolute or relative path. (Default: `"students.csv"`)
- `max_messages` (int): The maximum messages this script should send before quitting. Set to -1 to allow any number of messages. (Default: `-1`)
- `max_time` (string): The maximum time this script should run before quitting. Set to -1 to allow any amount of time. (Default: `"1h"`)
  - Allowed time units: `s`, `m`, `h`
- `min_delay` (int): The minimum time in seconds between sent messages. For example: if the first message is sent in 5 seconds, the program will wait 10 seconds before sending the next message (site loading times are included in this wait time). There will be no wait time between messages that took more than the configured time to send. (Default: `15`)
- `max_timeout` (int): The maximum time in seconds to wait for a page to load. If the process of sending a message takes longer than this time, either retry or quit execution. (Default: `30`)
- `max_retries` (int): The maximum number of times to retry sending a message before quitting execution. (Default: `5`)
- `handshake_url` (string): The url of the handshake instance to use. (Default: `"https://app.joinhandshake.com"`)
- `chromedriver_dir` (string): The filepath to the directory where the chromedriver executable is (chromedriver.exe). Can be an absolute or relative path. (Default: `"chromedriver-win64"`)

### message.txt

Create a file in the root of the project directory called `message.txt` and write the message you want to send to students. The message can be written in markdown and will be sent as a single paragraph. You can include any variable in the message with the name of the column from the students csv file surrounded by curly braces. For example: `{first_name}` will be replaced with the value of the `first_name` column for the student the message is being sent to.
