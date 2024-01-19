# MassHandshakeMessager - Change Log

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
