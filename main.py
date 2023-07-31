import touch
import display

def handle_activate(button):
    new_text = display.Text(f"Button {button} was tocuhed!", 0, 0, display.WHITE)
    display.show(new_text)

touch.callback(touch.A, handle_activate)

initial_text = display.Text("Start imaginging!", 0, 0, display.WHITE)
display.show(initial_text)