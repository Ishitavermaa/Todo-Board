# Minimal To-Do Board

A clean, minimalist to-do list that groups tasks into category columns. Add a heading, due date (with an optional time), category and description, then tick tasks off as you finish them.

## Features

- Board view with one column per category
- Due date with optional time, shown as overdue (red) or due today (amber)
- Live stats: total, due today, overdue, completed
- Filter by status or category, search, and sort by deadline, newest or A to Z
- Light and dark mode
- Tasks are saved automatically

## Files

| File | What it is |
| --- | --- |
| `todo_board.py` | Main app. A small Python server that opens the board in your browser. No installs needed. |
| `todo_board.html` | Standalone web version. Saves tasks in your browser, so it can be hosted on GitHub Pages. |
| `todo_app.py` | Earlier desktop version built with tkinter. |

## Run it

Requires Python 3.8 or newer.

```bash
python todo_board.py
```

It opens at http://localhost:8000. Your tasks are saved to `tasks.json` in the same folder.

## Use the web version

Open `todo_board.html` in any browser, or publish the repository with GitHub Pages (Settings > Pages) to get a link you can bookmark. Tasks are stored in that browser only.

## License

MIT
