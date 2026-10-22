"""Open a pop-up window asking for the room and the time.

Part of the analysis package; see the function's docstring for its input, output and errors.
"""

def ask_inputs(rooms):
    """Open a pop-up window asking for the room and the time.

    The room is chosen from a drop-down list of valid rooms (it cannot be typed). The
    window also has a time box (YYYY-MM-DD HH:MM) and OK / Cancel buttons. OK does
    nothing until a room is chosen. The time is checked later by get_headcount.

    Input:
        rooms: the room names to offer. It needs a computer with a screen.

    Output:
        A pair (room name, time text), or None if the window was cancelled or closed.

    Errors:
        ValueError if there are no rooms to offer.
    """
    import tkinter as tk
    from tkinter import ttk

    if not rooms:
        raise ValueError("There are no rooms to choose from.")
    window = tk.Tk()
    window.title("Room headcount")
    window.attributes("-topmost", True)
    answer = {}
    boxes = {name: tk.StringVar() for name in ("room", "time")}
    for row, text in enumerate(["Room", "Time (YYYY-MM-DD HH:MM)"]):
        tk.Label(window, text=text).grid(row=row, column=0, sticky="w", padx=8, pady=4)
    ttk.Combobox(window, textvariable=boxes["room"], values=list(rooms), state="readonly",
                 width=42).grid(row=0, column=1, padx=8, pady=4)
    tk.Entry(window, textvariable=boxes["time"], width=45).grid(row=1, column=1, padx=8, pady=4)

    def accept():
        if not boxes["room"].get():
            return
        answer["values"] = (boxes["room"].get(), boxes["time"].get().strip())
        window.destroy()

    tk.Button(window, text="OK", width=10, command=accept).grid(row=2, column=1, sticky="e", padx=8, pady=8)
    tk.Button(window, text="Cancel", width=10, command=window.destroy).grid(row=2, column=2, padx=8, pady=8)
    window.mainloop()
    return answer.get("values")
