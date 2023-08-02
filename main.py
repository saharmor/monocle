import touch
import display

def handle_activate(button):
    new_text = display.Text(f"Reimagining the scene ✨", 0, 0, display.WHITE)
    display.show(new_text)

def debug_message(msg: str):
    new_text = display.Text(msg, 0, 0, display.RED)
    display.show(new_text)

def show_message(msg: str):
    display_text = display.Text(msg, 0, 0, display.WHITE)
    display.show(display_text)

def take_pic(button):
    import camera
    import bluetooth

    # Capture a JPEG image and transfer it over the Bluetooth raw data service
    camera.capture()
    while data := camera.read(bluetooth.max_length()):
        bluetooth.send(data)
        
def take_pic2(button):
    import _camera
    import time
    import fpga
    import struct
    import bluetooth

    print('here')
    def capture():
        _camera.wake()
        print('here2')
        time.sleep_ms(1)
        fpga.write(0x1003, b"")
        print('here3')
        while fpga.read(0x1000, 1) == b"2":
            time.sleep_us(10)

    def read(bytes=254):
        if bytes > 254:
            raise ValueError("at most 254 bytes")

        avail = struct.unpack(">H", fpga.read(0x1006, 2))[0]

        if avail == 0:
            _camera.sleep()
            return None

        return fpga.read(0x1007, min(bytes, avail))

    # Capture a JPEG image and transfer it over the Bluetooth raw data service
    show_message('Capturing image...')
    capture()
    print('here4')
    while data := read(bluetooth.max_length()):
        bluetooth.send(data)
    
    show_message('Done capturing image!')


# touch.callback(touch.A, handle_activate)
touch.callback(touch.A, take_pic)

initial_text = display.Text("Let's go!", 0, 0, display.WHITE)
display.show(initial_text)