"""                                                                           
 _|    _|              _|      _|_|_|              _|      _|_|            
 _|    _|    _|_|    _|_|_|_|  _|    _|  _|  _|_|        _|      _|    _|  
 _|_|_|_|  _|    _|    _|      _|    _|  _|_|      _|  _|_|_|_|  _|    _|  
 _|    _|  _|    _|    _|      _|    _|  _|        _|    _|      _|    _|  
 _|    _|    _|_|        _|_|  _|_|_|    _|        _|    _|        _|_|_|  
                                                                       _|  
                                                                   _|_|    

    this code was written by 🍬 HotDrify
             hotdrify.t.me
"""
from simple_term_menu import TerminalMenu
import logging


def generate(
    options: list[str],
    title: str = None,
    styles: tuple[str] = ("bg_blue", "fg_black",),
    cursor: str = "# ",
    cursor_styles: tuple[str] = ("fg_blue",),
    select: bool = False,
    entries: bool = False
):
    """
    generate menu

    Params:
        options (list)
        title (str)
        styles (tuple)
        cursor (string)
        cursor_styles (tuple)
        select (boolean)

    Returns:
        index
    """
    menu_object = TerminalMenu(
        options,
        title=title,
        menu_cursor=cursor,
        menu_cursor_style=cursor_styles,
        menu_highlight_style=styles,
        multi_select=select,
    )

    index = menu_object.show()

    logging.debug(f"Menu index: {index}")

    return (
        index
        if not entries
        else
        menu_object.chosen_menu_entries
    )
