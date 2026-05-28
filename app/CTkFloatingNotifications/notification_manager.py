from .notification_panel import NotificationPanel
from .notification_type import NotifyType

class NotificationManager:
    def __init__(self, master):
        self._master = master
        self.notifications = []

    @property
    def master(self):
        return self._master

    @master.setter
    def master(self, value):
        self.clear_all()
        self._master = value

    def show_notification(self, message, notify_type=NotifyType.INFO, duration=5000, bg_color="#404040", text_color="#FFFFFF"):
        NotificationPanel(self._master, self, message, notify_type=notify_type, duration=duration, bg_color=bg_color, text_color=text_color)

    def add_notification(self, notification):
        self.notifications.append(notification)
        self.update_notification_positions()

    def remove_notification(self, notification):
        if notification in self.notifications:
            self.notifications.remove(notification)
        self.update_notification_positions()

    def clear_all(self):
        for notification in list(self.notifications):
            notification.cancel()
            try:
                notification.destroy()
            except Exception:
                pass
        self.notifications.clear()

    def update_notification_positions(self):
        for index, notification in enumerate(self.notifications):
            y_offset = -20 - (index * 70)
            notification.place(relx=1.0, rely=1.0, x=-20, y=y_offset, anchor="se")