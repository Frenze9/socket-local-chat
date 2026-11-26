import base64
import io
import os
import signal
import threading
from socket import socket, AF_INET, SOCK_STREAM

from customtkinter import *
from tkinter import filedialog
from PIL import Image


class MainWindow(CTk):
    BG = "#F5F9FF"
    CHAT_BG = "#FFFFFF"
    MENU_BG = "#DCEBFF"
    MENU_HOVER = "#C5DDFB"
    ACCENT = "#4A9BF5"
    ACCENT_HOVER = "#2F80E0"
    OTHER_BUBBLE = "#E3F0FF"
    BORDER = "#BBD7FA"
    TEXT = "#1F3A5F"
    HINT = "#7A93B3"

    MENU_CLOSED = 40
    MENU_OPEN = 200

    def __init__(self):
        super().__init__()

        set_appearance_mode("light")

        self.configure(fg_color=self.BG)
        self.geometry("700x500")
        self.title("Chat Client")

        self.username = "Artem"
        self.running = True

        self.label = None
        self.entry = None
        self.save_button = None

        # Handle window closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Side menu
        self.menu_frame = CTkFrame(
            self,
            width=self.MENU_CLOSED,
            height=300,
            fg_color=self.MENU_BG,
            corner_radius=0
        )
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)

        self.is_show_menu = False
        self.speed_animate_menu = -20
        self.menu_width = self.MENU_CLOSED

        self.btn = CTkButton(
            self,
            text="▶",
            command=self.toggle_show_menu,
            width=self.MENU_CLOSED,
            fg_color=self.MENU_BG,
            hover_color=self.MENU_HOVER,
            text_color=self.TEXT,
            corner_radius=0
        )
        self.btn.place(x=0, y=0)

        # Main chat area
        self.chat_field = CTkScrollableFrame(
            self,
            fg_color=self.CHAT_BG,
            corner_radius=12,
            scrollbar_button_color=self.BORDER,
            scrollbar_button_hover_color=self.ACCENT
        )
        self.chat_field.place(x=0, y=0)

        # Message input
        self.message_entry = CTkEntry(
            self,
            placeholder_text="Enter a message:",
            height=40,
            corner_radius=20,
            fg_color="#FFFFFF",
            border_color=self.BORDER,
            border_width=2,
            text_color=self.TEXT,
            placeholder_text_color=self.HINT
        )
        self.message_entry.place(x=0, y=0)

        # Send button
        self.send_button = CTkButton(
            self,
            text=">",
            width=50,
            height=40,
            corner_radius=20,
            fg_color=self.ACCENT,
            hover_color=self.ACCENT_HOVER,
            text_color="white",
            font=("Arial", 18, "bold"),
            command=self.send_message
        )
        self.send_button.place(x=0, y=0)

        # Image button
        self.open_img_button = CTkButton(
            self,
            text="📂",
            width=50,
            height=40,
            corner_radius=20,
            fg_color=self.MENU_BG,
            hover_color=self.MENU_HOVER,
            text_color=self.TEXT,
            command=self.open_image
        )
        self.open_img_button.place(x=0, y=0)

        # Enter to send messages
        self.bind_all("<Return>", self.on_enter)
        self.bind_all("<KP_Enter>", self.on_enter)

        self.adaptive_ui()

        # Socket connection
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("localhost", 8080))

            hello = (
                f"TEXT@{self.username}@"
                f"[SYSTEM] {self.username} joined the chat!\n"
            )

            self.sock.sendall(hello.encode("utf-8"))

            self.recv_thread = threading.Thread(
                target=self.recv_message,
                daemon=True
            )
            self.recv_thread.start()

        except OSError as e:
            self.add_message(f"Could not connect to the server: {e}")

    # Menu

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu = -abs(self.speed_animate_menu)
            self.btn.configure(text="▶")
            self.show_menu()

        else:
            self.is_show_menu = True
            self.speed_animate_menu = abs(self.speed_animate_menu)
            self.btn.configure(text="◀")
            self.show_menu()

            if self.label is None:
                self.label = CTkLabel(
                    self.menu_frame,
                    text="Name",
                    text_color=self.TEXT,
                    font=("Arial", 16, "bold")
                )
                self.label.pack(pady=30)

                self.entry = CTkEntry(
                    self.menu_frame,
                    placeholder_text="Your nickname...",
                    fg_color="#FFFFFF",
                    border_color=self.BORDER,
                    text_color=self.TEXT,
                    placeholder_text_color=self.HINT,
                    corner_radius=10
                )
                self.entry.pack(padx=10)

                self.save_button = CTkButton(
                    self.menu_frame,
                    text="Save",
                    command=self.save_name,
                    fg_color=self.ACCENT,
                    hover_color=self.ACCENT_HOVER,
                    text_color="white",
                    corner_radius=10
                )
                self.save_button.pack(pady=10, padx=10)

    def show_menu(self):
        self.menu_width = max(
            self.MENU_CLOSED,
            min(
                self.MENU_OPEN,
                self.menu_width + self.speed_animate_menu
            )
        )

        self.menu_frame.configure(width=self.menu_width)

        if self.is_show_menu and self.menu_width < self.MENU_OPEN:
            self.after(10, self.show_menu)

        elif not self.is_show_menu:
            if self.menu_width > self.MENU_CLOSED:
                self.after(10, self.show_menu)
            else:
                if self.label:
                    self.label.destroy()
                    self.label = None

                if self.entry:
                    self.entry.destroy()
                    self.entry = None

                if self.save_button:
                    self.save_button.destroy()
                    self.save_button = None

    def save_name(self):
        new_name = self.entry.get().strip()

        if new_name:
            self.username = new_name
            self.add_message(f"Your new nickname: {self.username}")

    # adaptive UI

    def adaptive_ui(self):
        if not self.running:
            return

        self.menu_frame.configure(height=self.winfo_height())

        self.chat_field.place(
            x=self.menu_width + 5,
            y=5
        )

        self.chat_field.configure(
            width=self.winfo_width() - self.menu_width - 30,
            height=self.winfo_height() - 60
        )

        self.send_button.place(
            x=self.winfo_width() - 55,
            y=self.winfo_height() - 45
        )

        self.message_entry.place(
            x=self.menu_width + 5,
            y=self.send_button.winfo_y()
        )

        self.message_entry.configure(
            width=self.winfo_width() - self.menu_width - 120
        )

        self.open_img_button.place(
            x=self.winfo_width() - 110,
            y=self.send_button.winfo_y()
        )

        self.after(50, self.adaptive_ui)

    def add_message(self, message, img=None, own=False):
        if not self.running:
            return

        bubble_color = self.ACCENT if own else self.OTHER_BUBBLE
        text_color = "white" if own else self.TEXT
        side = "e" if own else "w"

        message_frame = CTkFrame(
            self.chat_field,
            fg_color=bubble_color,
            corner_radius=14
        )

        message_frame.pack(
            pady=4,
            padx=6,
            anchor=side
        )

        wraplength_size = self.winfo_width() - self.menu_width - 90

        CTkLabel(
            message_frame,
            text=message,
            wraplength=wraplength_size,
            text_color=text_color,
            image=img,
            compound="top" if img else "none",
            justify="left",
            font=("Arial", 14)
        ).pack(padx=12, pady=7)

    # send and recv messages

    def on_enter(self, event):
        self.send_message()
        return "break"

    def send_message(self):
        message = self.message_entry.get().strip()

        if not message:
            return

        if not hasattr(self, "sock") or not self.running:
            self.add_message("Not connected to the server.")
            return

        data = f"TEXT@{self.username}@{message}\n"

        try:
            self.sock.sendall(data.encode("utf-8"))
            self.add_message(
                f"{self.username}: {message}",
                own=True
            )

        except OSError as e:
            self.add_message(f"Could not send message: {e}")

        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""

        while self.running:
            try:
                chunk = self.sock.recv(4096)

                if not chunk:
                    break

                buffer += chunk.decode(
                    "utf-8",
                    errors="ignore"
                )

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)

                    if self.running:
                        self.after(
                            0,
                            self.handle_line,
                            line.strip()
                        )

            except OSError:
                break

        if self.running:
            try:
                self.after(
                    0,
                    self.add_message,
                    "Disconnected from the server."
                )
            except RuntimeError:
                pass

    def handle_line(self, line):
        if not line or not self.running:
            return

        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]

                self.add_message(f"{author}: {message}")

        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                b64_img = parts[3]

                try:
                    img_data = base64.b64decode(b64_img)
                    pil_img = Image.open(
                        io.BytesIO(img_data)
                    )

                    ctk_img = CTkImage(
                        light_image=pil_img,
                        size=(300, 300)
                    )

                    self.add_message(
                        f"{author} sent an image: {filename}",
                        img=ctk_img
                    )

                except Exception as e:
                    self.add_message(
                        f"Error displaying image: {e}"
                    )

        else:
            self.add_message(line)

    # sending img

    def open_image(self):
        if not hasattr(self, "sock") or not self.running:
            self.add_message("Not connected to the server.")
            return

        file_name = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )

        if not file_name:
            return

        try:
            with open(file_name, "rb") as f:
                raw = f.read()

            b64_data = base64.b64encode(raw).decode("utf-8")
            short_name = os.path.basename(file_name)

            data = (
                f"IMAGE@{self.username}@"
                f"{short_name}@{b64_data}\n"
            )

            self.sock.sendall(data.encode("utf-8"))

            pil_img = Image.open(file_name)

            ctk_img = CTkImage(
                light_image=pil_img,
                size=(300, 300)
            )

            self.add_message(
                f"You sent an image: {short_name}",
                img=ctk_img,
                own=True
            )

        except OSError as e:
            self.add_message(f"Could not send the image: {e}")

    # closing

    def on_closing(self):
        if not self.running:
            return

        self.running = False

        if hasattr(self, "sock"):
            try:
                self.sock.shutdown(2)
            except OSError:
                pass

            try:
                self.sock.close()
            except OSError:
                pass

        self.destroy()


if __name__ == "__main__":
    win = MainWindow()

    def handle_interrupt(sig, frame):
        if win.running:
            try:
                win.after(0, win.on_closing)
            except RuntimeError:
                pass

    signal.signal(signal.SIGINT, handle_interrupt)
    win.mainloop()
