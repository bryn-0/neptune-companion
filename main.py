
import threading
import time
import output
import listen
import cv2

##START LISTENING METHOD BOOTS UP MAIN LISTENING LOOP
def start_listening():
    try:
        listen.main_listen()
    except Exception as e:
        print("Listen crashed:", e)


if __name__ == "__main__":
    print("Starting Neptune")

    output.start_media_loop()
    print("Display started")

    threading.Thread(target=listen.main_listen,daemon=True).start()
    print("Listening started")

    cv2.namedWindow("Neptune", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Neptune", output.WINDOW_W, output.WINDOW_H)

    while True:
        with output.lock:
            frame = output.current_frame

            if frame is not None:
                cv2.imshow("Neptune", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.01)