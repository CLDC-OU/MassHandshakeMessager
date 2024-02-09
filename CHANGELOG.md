# MassHandshakeMessager - Change Log

## Version 0.1.1 (Not Released Yet)

### Major Feature Changes

---

- Added a `stats.json` file to keep track of stats between script runs
  - Added the ability to keep track of the time the script has been running
  - Added the ability to keep track of the number of messages sent
  - Added the ability to keep track of the number of messages failed to send
  - Added the ability to keep track of the number of times retried/failed
  - Added the ability to keep track of the time spent sending messages
  - Added the ability to keep track of the time spent retrying
  - Added the ability to keep track of the current position in the `students.csv` file to keep track of where the script left off
- Added colorfully formatted stats retrieval and output functions
- Added ability for `stats` to be backed up
-

### Minor Feature Changes

---

- Logging Updates
  - Added console logging for each message sent
  - Added colorful console logging with the `colorama` library
  - Added the index of the student being messaged to logging
- Multiply the success rate by 100 to represent a percentage
- Added additional arguments to Chromedriver
  - Added a `--start-minimized` flag to the Chrome options to run Chrome minimized
  - Added a `--headless=new` flag to the Chrome options to run Chrome in headless mode
  - Added a `--disable-popup-blocking` flag to the Chrome options to run Chrome without popup blocking
  - Added a `enable-automation` flag to the Chrome options to run Chrome with automation enabled
  - Added a `--no-sandbox` flag to the Chrome options to run Chrome without a sandbox
  - Added a `--disable-dev-shm-usage` flag to the Chrome options to run Chrome without a shared memory file
  - Added a `--disable-browser-side-navigation` flag to the Chrome options to run Chrome without browser side navigation
  - Added a `--disable-gpu` flag to the Chrome options to run Chrome without a GPU
  - Added a `--disable-extensions` flag to the Chrome options to run Chrome without extensions
  - Added a `--disable-software-rasterizer` flag to the Chrome options to run Chrome without a software rasterizer to ensure the GPU process is disabled
- Added seconds rounding for output times to 2 decimal places
- Refactored properties in `messager.py` to use class properties with type checking
- Refactored `stats.json` file loading, writing, and updating to use the `utils.py` module

### Bug Fixes

---

- Fixed bug where script logged one more than the amount of times retried for a failed message
- Fixed bug where message was only partially typed in the message box by the time the script tried to send it (rubber banding)
- Fixed unintended behavior where script would take 5 minutes to retry if the page failed to load
- Fixed bug where script would not retry if the page failed to load
- Fixed memory leak where the script would take up more memory the longer it ran

## Version 0.1.0 (2024-01-19)

### Major Feature Changes

---

- Added the ability to send messages to students
- Added support for using a custom Chrome user data directory to handle sign in data
- Added support for a custom message
  - Added support for using variables in the message from the `students.csv` file
- Added `README.md` documentation
  - Added documentation for setting up the Chrome user data directory
  - Added documentation for installing dependencies
  - Added documentation for configuring the script
  - Added documentation for the `students.csv` file
  - Added documentation for the `config.json` file
  - Added documentation for the `message.txt` file
- Added report of script run results
  - Messages successfully sent
  - Time spent sending messages
  - Average time to send message
  - Success rate
  - Messages failed to send
  - Times failed/retried
  - Time spent retrying
  - Average time to retry
  - Time waited between messages
  - Average wait time
  - Time remaining before configuration cutoff
  - Messages remaining before configuration cutoff

### Minor Feature Changes

---

- Added support for a custom subject
- Added support for a maximum number of messages to send before stopping
- Added support for a maximum time to run before stopping
- Added support for a minimum delay between messages
- Added support for a random delay between messages
- Added support for a maximum time to wait for a page to load
- Added support for a maximum number of retries before skipping a student
- Added support for a custom Handshake url
- Added support for a custom chromedriver directory
- Added `requirements.txt` for installing dependencies
- Added `CHANGELOG.md`
- Added `LICENSE`
- Added example configuration files ([students.example.csv](students.example.csv), [config.example.json](config.example.json), [message.example.txt](message.example.txt))

### Bug Fixes

---

N/A
