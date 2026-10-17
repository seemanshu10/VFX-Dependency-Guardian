"""TEMPORARY debug helper: hover any part of the UI to see its variable name.

Remove by deleting this file and restoring `self.initUI()` in MainWindow.__init__.
"""
import sys

from PySide2.QtWidgets import QWidget, QLayout


def show_variable_tooltips(window, build_func):
    """Run build_func, then give every widget a tooltip with its variable name and layout chain."""
    module_name = type(window).__module__
    # id -> (object, name); keeping the object alive stops its id being reused
    names = {}

    def record_locals(frame, event, arg):
        # only look at the window's own build functions, as each one returns
        if event != "return" or frame.f_globals.get("__name__") != module_name:
            return
        for var_name, value in frame.f_locals.items():
            if var_name != "self" and isinstance(value, (QWidget, QLayout)):
                # outer functions return later, so their name overwrites a helper's generic one
                names[id(value)] = (value, var_name)

    previous_profiler = sys.getprofile()
    sys.setprofile(record_locals)
    try:
        build_func()
    finally:
        sys.setprofile(previous_profiler)

    # self.attributes are the names you actually use later, so they win over locals
    for attr_name, value in vars(window).items():
        if isinstance(value, (QWidget, QLayout)):
            names[id(value)] = (value, "self." + attr_name)

    # map each widget and sub-layout to the layout that holds it
    holder = {}
    for layout in window.findChildren(QLayout):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            child = item.widget() or item.layout()
            if child is not None:
                holder[id(child)] = layout

    def name_of(obj):
        return names.get(id(obj), (None, None))[1]

    for widget in window.findChildren(QWidget):
        var_name = name_of(widget)
        # unnamed internals (table viewport, scrollbars) fall back to their parent's tooltip
        if var_name is None:
            continue

        chain = []
        layout = holder.get(id(widget))
        while layout is not None:
            chain.append(name_of(layout) or type(layout).__name__)
            layout = holder.get(id(layout))

        text = f"{var_name}  ({type(widget).__name__})"
        if chain:
            text += "\nin: " + "  <  ".join(chain)
        widget.setToolTip(text)
