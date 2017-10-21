import ctypes
import logging

import camera
from error import Error

gp = ctypes.CDLL('libgphoto2.so.6')

"""
/**
 * \brief Type of the widget to be created.
 *
 * The actual widget type we want to create. The type of the value
 * it supports depends on this type.
 */
typedef enum {                                  /* Value (get/set): */
    GP_WIDGET_WINDOW,   /**< \brief Window widget
                 *   This is the toplevel configuration widget. It should
                 *   likely contain multiple #GP_WIDGET_SECTION entries.
                 */
    GP_WIDGET_SECTION,  /**< \brief Section widget (think Tab) */
    GP_WIDGET_TEXT,     /**< \brief Text widget. */         /* char *       */
    GP_WIDGET_RANGE,    /**< \brief Slider widget. */           /* float
*/
    GP_WIDGET_TOGGLE,   /**< \brief Toggle widget (think check box) */  /* int
*/
    GP_WIDGET_RADIO,    /**< \brief Radio button widget. */     /* char *
*/
    GP_WIDGET_MENU,     /**< \brief Menu widget (same as RADIO). */ /* char *
*/
    GP_WIDGET_BUTTON,   /**< \brief Button press widget. */     /*
CameraWidgetCallback */
    GP_WIDGET_DATE      /**< \brief Date entering widget. */        /* int
*/
} CameraWidgetType;
"""

GP_WIDGET_WINDOW = 0
GP_WIDGET_SECTION = 1
GP_WIDGET_TEXT = 2
GP_WIDGET_RANGE = 3
GP_WIDGET_TOGGLE = 4
GP_WIDGET_RADIO = 5
GP_WIDGET_MENU = 6
GP_WIDGET_BUTTON = 7
GP_WIDGET_DATE = 8
WidgetType = {
    GP_WIDGET_WINDOW: "window",
    GP_WIDGET_SECTION: "section",
    GP_WIDGET_TEXT: "text",
    GP_WIDGET_RANGE: "range",
    GP_WIDGET_TOGGLE: "toggle",
    GP_WIDGET_RADIO: "radio",
    GP_WIDGET_MENU: "menu",
    GP_WIDGET_BUTTON: "button",
    GP_WIDGET_DATE: "date"}


class Widget:
    """A camera configuration widget.

    See Config for the containg object.
    Widgets have type (eg. GP_WIDGET_RANGE, a value that
    can be set in a range perhaps with a slider), value (eg. 12.3), name (eg.
    "exposuresetting"), label (eg. "Camera Exposure") and, depending on the
    type, extra values you can grab such as (min, max, inc) via get_range().
    Widgets of type GP_WIDGET_SECTION and GP_WIDGET_WINDOW have children. Use
    get_children() to get a list of the child widgets.
    """

    def __init__(self, widget):
        """Wrap a Widget instance around the underlying gphoto2 pointer."""
        self.widget = widget

    def get_nchildren(self):
        return gp.gp_widget_count_children(self.widget)

    def get_child(self, i):
        child = ctypes.c_void_p()
        retval = gp.gp_widget_get_child(self.widget, i, ctypes.byref(child))
        if retval != camera.GP_OK:
            raise Error('Setting not found')
        return Widget(child)

    def get_child_by_name(self, name):
        child = ctypes.c_void_p()
        retval = gp.gp_widget_get_child_by_name(self.widget,
                                                name, ctypes.byref(child))
        if retval != camera.GP_OK:
            raise Error('Setting not found',
                        'Setting %s not in widget tree.' % name)
        return Widget(child)

    def get_children(self):
        """Return the children of this widget.

        Only SECTION and WINDOW widgets have children.
        """
        children = []
        for i in range(0, self.get_nchildren()):
            children += [self.get_child(i)]
        return children

    def get_wtype(self):
        """Return the type of the widget.
        Widgets may have the following types:
        GP_WIDGET_WINDOW = 0        the top widget
        GP_WIDGET_SECTION = 1       a group of related widgets
        GP_WIDGET_TEXT = 2          a string
        GP_WIDGET_RANGE = 3         see get_range()
        GP_WIDGET_TOGGLE = 4
        GP_WIDGET_RADIO = 5         see get_choices
        GP_WIDGET_MENU = 6          see get_choices
        GP_WIDGET_BUTTON = 7        not used
        GP_WIDGET_DATE = 8
        """
        wtype = ctypes.c_int()
        gp.gp_widget_get_type(self.widget, ctypes.byref(wtype))
        return wtype.value

    def get_name(self):
        """Return the name of the widget.
        Names are short, unique, text names which can be used to identity the
        widget. See Config.get_widget_by_name().
        """
        name = ctypes.c_char_p()
        gp.gp_widget_get_name(self.widget, ctypes.byref(name))
        return name.value

    def get_label(self):
        """Return the label of the widget.
        Labels are long, descriptive strings that can be shown to the user.
        """
        label = ctypes.c_char_p()
        gp.gp_widget_get_label(self.widget, ctypes.byref(label))
        return label.value

    def get_value(self):
        """Return the value of the widget.
        The value may be int for TOGGLE, float for RANGE, and a string for
        TEXT, MENU or RADIO.
        """
        wtype = self.get_wtype()
        if wtype == GP_WIDGET_TOGGLE:
            value = ctypes.c_int()
        elif wtype == GP_WIDGET_RANGE:
            value = ctypes.c_float()
        elif wtype in [GP_WIDGET_TEXT, GP_WIDGET_MENU, GP_WIDGET_RADIO]:
            value = ctypes.c_char_p()
        else:
            return None
        gp.gp_widget_get_value(self.widget, ctypes.byref(value))
        return value.value

    # there's info too, but it seems empty, at least for the Nikon

    def get_choices(self):
        """Return the possible choices for a RADIO or MENU widget."""
        nchoices = gp.gp_widget_count_choices(self.widget)
        choices = []
        for i in range(0, nchoices):
            choice = ctypes.c_char_p()
            gp.gp_widget_get_choice(self.widget, i, ctypes.byref(choice))
            choices += [choice.value]
        return choices

    def get_range(self):
        """Return a three-element float tuple of (min, max, inc) for the
        range.
        """
        wmin = ctypes.c_float()
        wmax = ctypes.c_float()
        winc = ctypes.c_float()
        gp.gp_widget_get_range(self.widget,
                               ctypes.byref(wmin),
                               ctypes.byref(wmax),
                               ctypes.byref(winc))
        return (wmin.value, wmax.value, winc.value)

    def get_readonly(self):
        """Return True for read-only widgets."""
        readonly = ctypes.c_int()
        gp.gp_widget_get_readonly(self.widget, ctypes.byref(readonly))
        return readonly.value

    def set_value(self, value):
        print "TEST"
        """Set the value of the widget.
        value should be float for RANGE, int for toggle and string for TEXT,
        MENU and RADIO.
        """
        wtype = self.get_wtype()
        if wtype == GP_WIDGET_RANGE:
            wvalue = ctypes.c_float()
        elif wtype == GP_WIDGET_TOGGLE:
            wvalue = ctypes.c_int()
        elif wtype in [GP_WIDGET_TEXT, GP_WIDGET_MENU, GP_WIDGET_RADIO]:
            wvalue = ctypes.c_char_p()
        else:
            return None
        wvalue.value = value
        logging.info('setting %s = %s', self.get_name(), str(wvalue.value))

        # for int/float, we have to pass a pointer to the object
        if wtype in [GP_WIDGET_RANGE, GP_WIDGET_TOGGLE]:
            wvalue = ctypes.byref(wvalue)
        gp.gp_widget_set_value(self.widget, wvalue)

    def set_changed(self, changed):
        wchanged = ctypes.c_int(changed)
        gp.gp_widget_set_changed(self.widget, wchanged)
        
    def json(self):
        return {'type': self.get_name(), 'options': self.get_choices(), 'value': self.get_value()}


class Config:
    """Load, modify and save camera configuration."""

    def __init__(self, camera):
        """Make a Config for a camera. See Camera."""
        self.camera = camera

        self.root_widget = None
        #finalize.track(self, self, self.free_config)

        self.refresh()

    def free_config(self):
        if self.root_widget:
            gp.gp_widget_free(self.root_widget)
            self.root_widget = ctypes.c_void_p()

    def refresh(self):
        self.camera.connect()

        self.free_config()
        self.root_widget = ctypes.c_void_p()
        retval = gp.gp_camera_get_config(self.camera.camera,
                                         ctypes.byref(self.root_widget), self.camera.context)
        if retval != camera.GP_OK:
            raise Error('Unable to get config')

    def get_root_widget(self):
        """Get the root Widget for a Config.

        Use this to iterate over all widgets. See Widget.
        """
        return Widget(self.root_widget)

    def set_config(self):
        """Write any modifications back to the camera.
        Make any modifications with Widget.set_value(), then write back with
        this.
        This method can raise camera.Error.
        """
        logging.debug('writing camera config ...')
        self.camera.connect()
        retval = gp.gp_camera_set_config(self.camera.camera,
                                         self.root_widget,
                                         self.camera.context)
        if retval != camera.GP_OK:
            raise Error('Unable to set config')

    def prettyprint(self, fp, widget, indent=0):
        """Prettyprint the camera settings to a File."""
        wtype = widget.get_wtype()
        label = widget.get_label()
        name = widget.get_name()

        fp.write('%s%s (%s) - %s\n' %
                 (' ' * indent, label, name, WidgetType[wtype]))

        if wtype == GP_WIDGET_RANGE:
            value = widget.get_value()
            wmin, wmax, winc = widget.get_range()
            fp.write('%s(value = %f, min = %f, max = %f, inc = %f)\n' %
                     (' ' * indent, value, wmin, wmax, winc))

        if wtype == GP_WIDGET_TOGGLE:
            value = widget.get_value()
            fp.write('%s(value = %d)\n' % (' ' * indent, value))

        if wtype == GP_WIDGET_TEXT:
            value = widget.get_value()
            fp.write('%s(value = %s)\n' % (' ' * indent, value))

        if wtype == GP_WIDGET_MENU or wtype == GP_WIDGET_RADIO:
            value = widget.get_value()
            choices = widget.get_choices()
            fp.write('%s(value = %s, choices = %s)\n' %
                     (' ' * indent, value, choices))

        # ignore DATE, it's fiddly
        # WINDOW is only for the top-level, BUTTON is never used
        # SECTION just encloses children

        for child in widget.get_children():
            self.prettyprint(fp, child, indent + 2)


