"""Open a pop-up window asking which optional plots to show.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

PLOT_CHOICES = {
    "new": "New data: the model built from your data over that day's raw readings",
    "training": "Training data: the saved model over that day's raw readings (needs the preprocessed training data)",
}


def ask_plots(choices=None):
    """Open a pop-up window with a tick box for each optional plot.

    Input:
        choices: optional. A dictionary of plot key to the text shown (default: PLOT_CHOICES).
            Pass only the plots that are available, e.g. without "new" when no data file was given.
        It needs a computer with a screen.

    Output:
        A list of the chosen plot keys ("new", "training"), possibly empty.
        Cancelling or closing the window gives an empty list (no plots).

    Errors:
        None.
    """
    import tkinter as tk

    choices = PLOT_CHOICES if choices is None else choices
    window = tk.Tk()
    window.title("Optional plots")
    window.attributes("-topmost", True)
    ticks = {key: tk.BooleanVar(value=False) for key in choices}
    tk.Label(window, text="Show any of these plots?").grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=6)
    for row, (key, text) in enumerate(choices.items(), start=1):
        tk.Checkbutton(window, text=text, variable=ticks[key]).grid(row=row, column=0, columnspan=2, sticky="w", padx=8)
    answer = []

    def accept():
        answer.extend(key for key, tick in ticks.items() if tick.get())
        window.destroy()

    tk.Button(window, text="Show", width=10, command=accept).grid(row=len(choices) + 1, column=0, padx=8, pady=8)
    tk.Button(window, text="No plots", width=10, command=window.destroy).grid(row=len(choices) + 1, column=1, padx=8, pady=8)
    window.mainloop()
    return answer
