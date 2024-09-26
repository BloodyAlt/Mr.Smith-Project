import os
import cv2

window_title = 'Mr. Smith'

base_dir = os.path.dirname(os.path.abspath(__file__))
resources_dir = os.path.join(base_dir, 'resources')

def play_video(video_file):
    video_path = os.path.join(resources_dir, video_file)
    video = cv2.VideoCapture(video_path)
    
    if not video.isOpened():
        print("Error opening video file")
        return

    while video.isOpened():
        ret, frame = video.read()
        
        if not ret:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        if ret:
            cv2.imshow(window_title, frame)
            keycode = cv2.waitKey(24) & 0xFF
            
            # Toggle fullscreen with 'f'
            if keycode == ord('f'):
                switch_fullscreen()
            
            # Exit with 'Esc'
            if keycode == 27:
                break

            # Close if the window is closed manually
            if cv2.getWindowProperty(window_title, cv2.WND_PROP_VISIBLE) < 1:
                break
        else:
            break

    # Release resources when done
    video.release()
    cv2.destroyAllWindows()

def switch_fullscreen():
    isFull = cv2.getWindowProperty(window_title, cv2.WND_PROP_FULLSCREEN)
    
    if isFull == 1:
        cv2.setWindowProperty(window_title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    else:
        cv2.setWindowProperty(window_title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

def main():
    # Create the window
    cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)

    # Set the initial window size to 1920x1080
    cv2.resizeWindow(window_title, 1920, 1080)
    
    # Keep the window open even if no video is playing
    while True:
        # Check for key press to quit the window with 'Esc'
        keycode = cv2.waitKey(24) & 0xFF
        
        # Play video
        play_video("videos/smith_s2.mp4")
        
        # Toggle fullscreen with 'f'
        if keycode == ord('f'):
            switch_fullscreen()

        # Exit with 'Esc'
        if keycode == 27:
            break
        
        # Close if the window is closed manually
        if cv2.getWindowProperty(window_title, cv2.WND_PROP_VISIBLE) < 1:
            break
    
    # Cleanup
    cv2.destroyAllWindows()

main()
