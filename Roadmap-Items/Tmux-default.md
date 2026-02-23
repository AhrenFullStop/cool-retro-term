This is a cool retro terminal app that we compile from source and use as a `.app` file on macOS.

The tast is to improve the app for our usecase.

Currently, Everytime I startup this terminal I have to manually initialize tmux by invoking the tmux command. I want it to startup with tmux enabled by default.

- we should also have right click menu for tmux options (already present by default)
- I must be able to copy text from the terminal using the mouse cursor. This is hyper NB and currently is not working from the context of a tmux session/terminal running in the terminal.

Right now I can hilight some text, as soon as i let go of the mouse button the text is no longer selected and I cannot copy it. If i copy it while holding the key, I can visually see the "Edit" > "Copy" action happening from keypress (the context menu hilights briefly to indicate that the action was registered) but the text is not copied to the clipboard. I have tested this in a normal terminal (not tmux) and it works as expected. I have also tested this in a tmux session running in a normal terminal and it works as expected. This is only happening in the context of a tmux session/terminal running in the cool-retro terminal.