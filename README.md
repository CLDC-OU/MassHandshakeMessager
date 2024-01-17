# MassHandshakeMessager

Automate Career Services sending mass messages to students on [Handshake](https://joinhandshake.com/)

## Setup

1. Login to Handshake in a Chrome browser instance
2. Ensure all [Dependencies](#dependencies) have been installed
3. Complete the [Configuration](#configuration)

## Chrome User Data Directory

To eliminate the need to store login credentials in a config file (and risk getting locked behind 2FA), this script will inject a specified user data directory into a new instance of Chrome already signed in to Handshake to use for sending messages. This new instance of Chrome will be completely separate from the normal instance used for browsing and will be deleted after the script is run to ensure there are no external effects.

> [!IMPORTANT]
>
> Make sure you are logged in to Handshake in the correct instance of Chrome being used for the data directory before running the script.

By default, Chrome stores user data in the following directories: `%HOMEPATH%\AppData\Local\Google\Chrome\User Data` on Windows and `~/Library/Application Support/Google/Chrome` on Mac.

It is recommended to use a custom Chrome user data directory for this script. This will ensure that any changes to your browser settings that might occur during normal browsing (cookies, logins, etc.) will not affect the script.

> [!NOTE]
>
> You can find the directory of your Chrome instance by going to `chrome://version` in the address bar of your Chrome instance and looking for the `Profile Path` property.

### Default Chrome User Data Directory

If you are using the default Chrome user data directory (i.e., the same Chrome browser you use for normal browsing), make sure to set the `chrome_data_dir` property in the `config.json` file to the correct directory for your operating system (more information in [Configuration](#configuration)).

> [!WARNING]
>
> If you are using the default Chrome user data directory, you must make sure you are logged in to Handshake to the right account on the Career Services side before running the script. If you are logged in to the wrong account, you will be sending messages from the wrong account.

### Custom Chrome User Data Directory

If you are using a custom Chrome instance, make sure to set the `chrome_data_dir` property in the `config.json` file to the correct directory of your Chrome user data (more information in [Configuration](#configuration)).

> [!NOTE]
>
> You can create a new Chrome instance by creating a new directory and running Chrome with the `--user-data-dir` flag. For example: `chrome.exe --user-data-dir="C:\Chrome User Data"` on Windows or `open -a "Google Chrome" --args --user-data-dir="/Chrome User Data"` on Mac.

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
