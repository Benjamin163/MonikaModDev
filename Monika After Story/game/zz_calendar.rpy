# Calendar module
# A custom made Calendar like UI to help managing date based events

# TODO: add a calendar overlay and a calenar sprite to the background.
# the background sprite is just attached to the spaceroom bg.
#
# the calendar overlay will have an empty idle image but a highlighted hover
# image. It will only be enabled during idle modes (allow_dialgoue) and will
# enable user to go straight to view mode of the calendar.

init python:



    class MASCalendar(renpy.Displayable):
        """
        Custom Calendar UI, can be used to display the events that are dependent
        on dates or to allow user to pick a date

        """

        import pygame
        import datetime
        import store.evhand as evhand

        # CONSTANTS

        # view port size
        VIEW_WIDTH = 1280
        VIEW_HEIGHT = 720

        # exit button position and size
        EXIT_BUTTON_WIDTH = 74
        EXIT_BUTTON_HEIGHT = 74
        EXIT_BUTTON_X = 1040
        EXIT_BUTTON_Y = 60

        # day name related sizes
        DAY_BUTTON_WIDTH = 128
        DAY_BUTTON_HEIGHT = 65
        DAY_NAME_BUTTON_HEIGHT = 35

        # initial position for displaying things inside the calendar
        INITIAL_POSITION_X = 193
        INITIAL_POSITION_Y = 155

        # position for the title
        TITLE_POSITION_Y = 115
        TITLE_POSITION_X_1 = 560
        TITLE_POSITION_X_2 = 530

        # size for the arrow like button selectors
        ARROW_BUTTON_SIZE = 20

        # Size of the day number and displayed data inside a day block
        CALENDAR_DAY_TEXT_SIZE = 12

        # X inside the close button size
        CALENDAR_CLOSE_X_SIZE = 45

        # Return values for constant buttons
        CALENDAR_CLOSE = "CLOSE" # closes the calendar
        CALENDAR_MONTH_INCREASE = "MONTH_INCR" # signals to increase the current selected month
        CALENDAR_MONTH_DECREASE = "MONTH_DECR" # signals to decrease the current selected month
        CALENDAR_YEAR_INCREASE = "YEAR_INCR" # signals to increase the current selected year
        CALENDAR_YEAR_DECREASE = "YEAR_DECR" # signals to decrease the current selected month

        # Color used for the day number
        TEXT_DAY_COLOR = "#000000" # PINK: "#ffb0ed"

        # Month names constant array
        MONTH_NAMES = ["Unknown", "January", "Febuary",
            "March", "April", "May", "June", "July",
            "August", "September", "October",
            "November", "December"]

        # Day names constant array
        DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday"]

        # Format used for calendar display
        DATE_DISPLAY_FORMAT = "\t  \t  \t  \t  \t  \t  \t  {0}\n{1}\n{2}\n{3}"

        # Events to which Calendar buttons will check for
        MOUSE_EVENTS = (
            pygame.MOUSEMOTION,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEBUTTONDOWN
        )


        def __init__(self, select_date=False):
            """
            Constructor for the custom calendar.

            IN:
                select_date - a boolean that indicates how this calendar is going to
                    do, True indicates that it will select a day, False means that it
                    will only be for displaying events.
                    (Default: False)
            """
            super(renpy.Displayable, self).__init__()

            # The calendar background
            self.calendar_background = renpy.displayable("mod_assets/calendar/calendar_bg.png")

            # Can we select dates?
            self.can_select_date = select_date

            # database
            self.database = evhand.calendar_database

            # background mask
            self.background = Solid(
                "#000000B2",
                xsize=self.VIEW_WIDTH,
                ysize=self.VIEW_HEIGHT
            )

            # default calendar view to current month
            # keep reference to it in case it may need it later
            self.today = datetime.date.today()

            self.selected_month = self.today.month
            self.selected_year = self.today.year

            # store all buttons for easy rendering
            self.const_buttons = []
            self.day_buttons = []

            # button backgrounds
            button_close = Image(
                "mod_assets/calendar/calendar_close.png"
            )
            button_day_name = Image(
                "mod_assets/calendar/calendar_day_name_bg.png"
            )
            button_left_arrow = Image(
                "mod_assets/calendar/calendar_left_arrow.png"
            )
            button_right_arrow = Image(
                "mod_assets/calendar/calendar_right_arrow.png"
            )

            # Change title depending on flag
            if select_date:
                self.title_position_x = self.TITLE_POSITION_X_2
                self.text_title = Text(
                    "Select a Date",
                    font=gui.default_font,
                    size=33,
                    color="#ffffff",
                    outlines=[]
                )
            else:
                self.title_position_x = self.TITLE_POSITION_X_1
                self.text_title = Text(
                    "Calendar",
                    font=gui.default_font,
                    size=33,
                    color="#ffffff",
                    outlines=[]
                )

            # iterate over the days
            i = 0
            for day in self.DAY_NAMES:

                # Generate as buttons the day names

                button_day_text = Text(
                    day,
                    font=gui.default_font,
                    size=17,
                    color=self.TEXT_DAY_COLOR,
                    outlines=[]
                )

                button_day_button = MASButtonDisplayable(
                    button_day_text,
                    button_day_text,
                    button_day_text,
                    button_day_name,
                    button_day_name,
                    button_day_name,
                    self.INITIAL_POSITION_X + (i * self.DAY_BUTTON_WIDTH),
                    self.INITIAL_POSITION_Y + self.DAY_NAME_BUTTON_HEIGHT,
                    self.DAY_BUTTON_WIDTH,
                    self.DAY_NAME_BUTTON_HEIGHT,
                    hover_sound=None,
                    activate_sound=None,
                    return_value=None
                )

                # add them to the const_buttons array
                self.const_buttons.append(button_day_button)
                i = i + 1

            # close button
            button_text_close = Text(
                "X",
                font=gui.default_font,
                size=self.CALENDAR_CLOSE_X_SIZE,
                color="#ffb0ed",
                outlines=[]
            )

            self.button_exit = MASButtonDisplayable(
                button_text_close,
                button_text_close,
                button_text_close,
                button_close,
                button_close,
                button_close,
                self.EXIT_BUTTON_X,
                self.EXIT_BUTTON_Y,
                self.EXIT_BUTTON_WIDTH,
                self.EXIT_BUTTON_HEIGHT,
                hover_sound=gui.hover_sound,
                activate_sound=gui.activate_sound,
                return_value=self.CALENDAR_CLOSE
            )

            # empty text label used for the buttons that require an image
            # these aren't Image buttons mostly cause I find easier to keep
            # it constant with the UI related buttons
            button_empty_text = Text(
                "",
                font=gui.default_font,
                size=12,
                color="#ffb0ed",
                outlines=[]
            )

            # actual buttons that decrease/ increase the month and year values
            self.button_month_decrease = MASButtonDisplayable(
                button_empty_text,
                button_empty_text,
                button_empty_text,
                button_left_arrow,
                button_left_arrow,
                button_left_arrow,
                self.INITIAL_POSITION_X + 70,
                self.INITIAL_POSITION_Y + 10,
                self.ARROW_BUTTON_SIZE,
                self.ARROW_BUTTON_SIZE,
                hover_sound=gui.hover_sound,
                activate_sound=gui.activate_sound,
                return_value=self.CALENDAR_MONTH_DECREASE
            )

            self.button_month_increase = MASButtonDisplayable(
                button_empty_text,
                button_empty_text,
                button_empty_text,
                button_right_arrow,
                button_right_arrow,
                button_right_arrow,
                self.INITIAL_POSITION_X + 300,
                self.INITIAL_POSITION_Y + 10,
                self.ARROW_BUTTON_SIZE,
                self.ARROW_BUTTON_SIZE,
                hover_sound=gui.hover_sound,
                activate_sound=gui.activate_sound,
                return_value=self.CALENDAR_MONTH_INCREASE
            )

            self.button_year_decrease = MASButtonDisplayable(
                button_empty_text,
                button_empty_text,
                button_empty_text,
                button_left_arrow,
                button_left_arrow,
                button_left_arrow,
                self.INITIAL_POSITION_X + 525,
                self.INITIAL_POSITION_Y + 10,
                self.ARROW_BUTTON_SIZE,
                self.ARROW_BUTTON_SIZE,
                hover_sound=gui.hover_sound,
                activate_sound=gui.activate_sound,
                return_value=self.CALENDAR_YEAR_DECREASE
            )

            self.button_year_increase = MASButtonDisplayable(
                button_empty_text,
                button_empty_text,
                button_empty_text,
                button_right_arrow,
                button_right_arrow,
                button_right_arrow,
                self.INITIAL_POSITION_X + 770,
                self.INITIAL_POSITION_Y + 10,
                self.ARROW_BUTTON_SIZE,
                self.ARROW_BUTTON_SIZE,
                hover_sound=gui.hover_sound,
                activate_sound=gui.activate_sound,
                return_value=self.CALENDAR_YEAR_INCREASE
            )

            # add buttons to the const_buttons array
            self.const_buttons.append(self.button_exit)
            self.const_buttons.append(self.button_month_decrease)
            self.const_buttons.append(self.button_month_increase)
            self.const_buttons.append(self.button_year_decrease)
            self.const_buttons.append(self.button_year_increase)

            # call set up day buttons to fill up the calendar
            self._setupDayButtons()


        def _setupDayButtons(self):
            """
            Sets up the day buttons used in the calendar
            """

            # button backgrounds
            button_day_bg = Image(
                "mod_assets/calendar/calendar_day_bg.png"
            )

            button_day_bg_disabled = Image(
                "mod_assets/calendar/calendar_day_disabled_bg.png"
            )


            # constant month and year text labels
            self.text_current_month = Text(
                self.MONTH_NAMES[self.selected_month],
                font=gui.default_font,
                size=21,
                color=self.TEXT_DAY_COLOR,
                outlines=[]
            )

            self.text_current_year = Text(
                str(self.selected_year),
                font=gui.default_font,
                size=21,
                color=self.TEXT_DAY_COLOR,
                outlines=[]
            )

            # init day buttons array
            self.day_buttons = []

            # get relevant date info
            day = datetime.timedelta(days=1)
            first_day = datetime.datetime(self.selected_year, self.selected_month, 1)

            # get the first_day of the week that has the first day of current month
            while first_day.weekday() != 6:
                first_day = first_day - day

            # init the array that will hold the dates we're displaying
            self.dates = []

            # get all the dates we'll be displaying  and store them on the array
            for i in range(42):
                self.dates.append(first_day + datetime.timedelta(days=i))

            # get this month's events
            events = self.database[self.selected_month]

            # calculation to determine the initial y position
            initial_y = self.INITIAL_POSITION_Y + (self.DAY_NAME_BUTTON_HEIGHT * 2)

            # iterate over rows and columns to create our calendar ui
            for i in range(6):

                for j in range(7):

                    # helper vars for day processing
                    current_date = self.dates[j + (i * 7)]
                    ret_val = None

                    # current day events display helpers
                    event_labels = list()
                    third_label = ""

                    # if this day is on the current month process the events that it may have
                    if current_date.month == self.selected_month:
                        # iterate through them
                        for e in events[current_date.day]:

                            # if the year is None or it's equal
                            # TODO maybe make it a list?
                            if not e[2] or e[2] == self.selected_year:

                                # add it to the event labels
                                if e[0] is Event:
                                    event_labels.append(e[1])
                                # add here specific processing depending on type

                        # if we have exactly 3 events
                        if len(event_labels) == 3:
                            # third_label should hold the event text
                            third_label = event_labels[2]
                        if len(event_labels) > 3:
                            # TODO we need to return something to force trigger the
                            # scrollable pane with full event, either the events[current_date.day]
                            # or event_labels
                            third_label = "see more"

                    # if we don't have any labels or less than 2
                    if not event_labels or len(event_labels) < 2:

                        # we can safely add 2 empty ones
                        event_labels.append("")
                        event_labels.append("")

                    # Add button behaviour to it
                    if self.can_select_date and current_date.month == self.selected_month:
                        ret_val = current_date

                    day_button_text = Text(
                        self.DATE_DISPLAY_FORMAT.format(str(current_date.day), event_labels[0], event_labels[1], third_label),
                        font=gui.default_font,
                        size=self.CALENDAR_DAY_TEXT_SIZE,
                        color=self.TEXT_DAY_COLOR,
                        outlines=[]
                    )

                    day_button = MASButtonDisplayable(
                        day_button_text,
                        day_button_text,
                        day_button_text,
                        button_day_bg,
                        button_day_bg,
                        button_day_bg_disabled,
                        self.INITIAL_POSITION_X + (j * self.DAY_BUTTON_WIDTH),
                        initial_y + (i * self.DAY_BUTTON_HEIGHT),
                        self.DAY_BUTTON_WIDTH,
                        self.DAY_BUTTON_HEIGHT,
                        hover_sound=gui.hover_sound,
                        activate_sound=gui.activate_sound,
                        return_value=ret_val
                    )

                    # if this day isn't on the current month
                    if current_date.month != self.selected_month:
                        # disable the button
                        day_button.disable()


                    self.day_buttons.append(day_button)


        def _xcenter(self, v_width, width):
            """
            Returns the appropriate X location to center an object with the
            given width

            IN:
                v_width - width of the view
                width - width of the object to center

            RETURNS:
                appropiate X coord to center
            """
            return int((v_width - width) / 2)


        def _buttonSelect(self, ev, x, y, st):
            """
            Goes through the list of buttons and return the first non-None
            value returned

            RETURNS:
                first non-none value returned
            """

            #iterate over both lists
            for button in self.const_buttons:
                ret_val = button.event(ev, x, y, st)
                if ret_val:
                    return ret_val

            for button in self.day_buttons:
                ret_val = button.event(ev, x, y, st)
                if ret_val:
                    return ret_val

            return None


        def _changeYear(self, ascend=True):
            """
            Changes the currently selected year by incrementing or decrementing it by one
            and refreshes the view

            IN:
                ascend - flag that indicates wheter increment or decrement
                    (Defaults to True)
            """
            if ascend:
                self.selected_year = self.selected_year + 1
            else:
                self.selected_year = self.selected_year - 1
            self._setupDayButtons()


        def _changeMonth(self, ascend=True):
            """
            Changes the currently selected month by incrementing or decrementing it by one
            and refreshes the view

            IN:
                ascend - flag that indicates wheter increment or decrement
                    (Defaults to True)
            """
            if ascend:

                self.selected_month = self.selected_month + 1

                # check if we need to increment the year
                if self.selected_month >=13:
                    self.selected_month = 1
                    self.selected_year = self.selected_year + 1
            else:

                self.selected_month = self.selected_month - 1

                # check if  we need to decrement the year
                if self.selected_month <=0:
                    self.selected_month = 12
                    self.selected_year = self.selected_year - 1
            self._setupDayButtons()


        def render(self, width, height, st, at):

            # render mask
            back = renpy.render(self.background, width, height, st, at)

            # Create a render for the background.
            calendar_bg = renpy.render(self.calendar_background, width, height, st, at)

            # Calendar title
            calendar_title = renpy.render(self.text_title, width, height, st, at)

            # displayable month and year labels
            month_label = renpy.render(self.text_current_month, width, height, st, at)

            year_label = renpy.render(self.text_current_year, width, height, st, at)

            # now do some calcs
            monw, monh = month_label.get_size()
            yearw, yearh = year_label.get_size()

            monthx = self._xcenter(380, monw)
            yearx = self._xcenter(380, yearw) + 460

            # Get the size of the child.
            self.width, self.height = calendar_bg.get_size()

            # Create the render we will return.
            r = renpy.Render(width, height)

            # blit the constant elements that make this UI
            r.blit(back,(0,0))

            r.blit(calendar_bg, (192, 103))

            r.blit(month_label, (self.INITIAL_POSITION_X + monthx, self.INITIAL_POSITION_Y + 8))

            r.blit(year_label, (self.INITIAL_POSITION_X + yearx, self.INITIAL_POSITION_Y + 8))

            r.blit(calendar_title, (self.title_position_x, self.TITLE_POSITION_Y))

            # blit the constant buttons
            c_r_buttons = [
                (
                    x.render(width, height, st, at),
                    (x.xpos, x.ypos)
                )
                for x in self.const_buttons
            ]

            for vis_b, xy in c_r_buttons:
                r.blit(vis_b, xy)

            # blit the calendar buttons
            cal_r_buttons = [
                (
                    x.render(width, height, st, at),
                    (x.xpos, x.ypos)
                )
                for x in self.day_buttons
            ]

            for vis_b, xy in cal_r_buttons:
                r.blit(vis_b, xy)

            # Return the render.
            return r


        def event(self, ev, x, y, st):

            # we only care about mouse
            if ev.type in self.MOUSE_EVENTS:

                # get the value from buttons
                sel_action = self._buttonSelect(ev, x, y, st)

                if sel_action:

                    # nonNone value returned

                    if sel_action == self.CALENDAR_CLOSE:

                        # this means the user selected close
                        return ""

                    #if we have a datetime
                    if isinstance(sel_action, datetime.datetime):

                        # return it
                        return sel_action

                    # check for month/year decrements and increments
                    if sel_action == self.CALENDAR_YEAR_INCREASE:
                        self._changeYear()

                    if sel_action == self.CALENDAR_YEAR_DECREASE:
                        self._changeYear(False)

                    if sel_action == self.CALENDAR_MONTH_INCREASE:
                        self._changeMonth()

                    if sel_action == self.CALENDAR_MONTH_DECREASE:
                        self._changeMonth(False)

            # otherwise continue
            renpy.redraw(self, 0)
            raise renpy.IgnoreEvent()

# wrap it up in a screen
screen mas_calendar_screen(select_date=False):

    zorder 51

    add MASCalendar(select_date)
        #xalign 0.5
        #yalign 0.5

# labels for easy testing
label mas_start_calendar(select_date=False):

    call screen mas_calendar_screen(select_date)

    # return value?
    if _return:

        m "got a return value [_return]"
        return _return

    m "No returned value"

    return

label mas_start_calendar_select(select_date=True):

    call screen mas_calendar_screen(select_date)

    # return value?
    if _return:

        m "got a return value [_return]"
        return _return

    m "No returned value"

    return
