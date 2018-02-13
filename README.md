# Rita Heallis
A scheduling helper. A robot. A hero.

This program is intended to help coordinate meetings between many people who use very different scheduling systems.

**Warning: has only been tested with Python 3!!**

## Installation
Preferably inside some virtual/conda env, run this in a terminal:
```
pip install
```

## Usage
To generate your availability in CSV format run this in a terminal:
```
rita
```
You will be asked a series of questions about when you're available.
Most of them will have default answers shown in square brackets.
You can hit `Enter` to accept these defaults.

At the end Rita will produce a CSV file for you.
Once we have the files for everybody, we'll analyze them with Rita.

## Known Issues
Rita is currently very much a prototype.
There is basically no input validation/verification.
As a consequence at least these "bugs" have been observed

- Time intervals aren't checked for validity. I don't know what happens if you put in "13 9" as an interval.
- Individual times aren't checked either. You could enter 9999 and it would silently be ignored.
- You can enter any date whatsoever for the exceptional days, it doesn't need to be the day of the week in question.
