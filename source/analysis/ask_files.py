"""Open a pop-up asking for the new files, if there are any.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

def ask_files():
    """Open a pop-up asking for the new files, if there are any.

    The window has two optional file rows, each with a "Browse..." button: new
    headcount data, and a room lookup. Leaving both empty means "no new files".
    Buttons: "Continue" and "Cancel".

    Input:
        None. (It needs a computer with a screen.)

    Output:
        A pair (headcount file, lookup file). Each is the file's path as text, or ""
        if none was chosen. None if the window was cancelled or closed.
    """
    import tkinter as tk
    from tkinter import filedialog

    window = tk.Tk()
    window.title("New files")
    window.attributes("-topmost", True)
    answer = {}
    chosen = {"data": tk.StringVar(), "lookup": tk.StringVar()}
    for row, (key, text) in enumerate([("data", "New headcount data (optional)"),
                                       ("lookup", "Updated room lookup (optional)")]):
        tk.Label(window, text=text).grid(row=row, column=0, sticky="w", padx=8, pady=4)
        tk.Entry(window, textvariable=chosen[key], width=50).grid(row=row, column=1, padx=8, pady=4)

        def browse(key=key):
            picked = filedialog.askopenfilename(parent=window, filetypes=[("CSV files", "*.csv")])
            if picked:
                chosen[key].set(picked)

        tk.Button(window, text="Browse...", command=browse).grid(row=row, column=2, padx=8)

    def accept():
        answer["value"] = (chosen["data"].get().strip(), chosen["lookup"].get().strip())
        window.destroy()

    buttons = tk.Frame(window)
    buttons.grid(row=2, column=0, columnspan=3, pady=8)
    tk.Button(buttons, text="Continue", width=10, command=accept).pack(side="left", padx=4)
    tk.Button(buttons, text="Cancel", width=10, command=window.destroy).pack(side="left", padx=4)
    window.mainloop()
    return answer.get("value")
