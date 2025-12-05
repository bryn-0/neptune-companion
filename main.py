import threading
import time
import output

IS_PI = output.IS_PI

def start_listening():
    import listen
    try:
        listen.main_listen()
    except Exception as e:
        print("Listen crashed:", e)


if __name__ == "__main__":
    print("Starting Neptune")

    output.start_media_loop()
    print("Media loop started")

    threading.Thread(target=start_listening, daemon=True).start()
    print("Listening started")

    if not IS_PI:
        # CV2 preview window on Mac/PC
        import cv2
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
        cv2.destroyAllWindows()
    else:
        # Pi: VLC handles display, loop until exit
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Shutting down Neptune...")
