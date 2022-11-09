from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import datetime
import calendar


def create_callback_data(action, year, month, day):
    """ Create the callback data associated to each button"""
    return "-".join([action, str(year), str(month), str(day)])


def create_calendar(year=None, month=None):
    """
    Create an inline keyboard with the provided year and month
    :param int year: Year to use in the calendar, if None the current year is used.
    :param int month: Month to use in the calendar, if None the current month is used.
    :return: Returns the InlineKeyboardMarkup object with the calendar.
    """
    now = datetime.datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    data_ignore = create_callback_data("IGNORE", year, month, 0)
    keyboard = []
    # First row - Month and Year
    row = [InlineKeyboardButton(calendar.month_name[month] + " " + str(year), callback_data=data_ignore)]
    keyboard.append(row)
    # Second row - Week Days
    row = []
    for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
        row.append(InlineKeyboardButton(day, callback_data=data_ignore))
    keyboard.append(row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data=data_ignore))
            else:
                row.append(InlineKeyboardButton(str(day), callback_data=create_callback_data("DAY", year, month, day)))
        keyboard.append(row)
    # Last row - Buttons
    row = [InlineKeyboardButton("<", callback_data=create_callback_data("PREV-MONTH", year, month, day)),
           InlineKeyboardButton(" ", callback_data=data_ignore),
           InlineKeyboardButton(">", callback_data=create_callback_data("NEXT-MONTH", year, month, day))]
    keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)
