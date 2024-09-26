import os
import cv2

base_dir = os.path.dirname(os.path.abspath(__file__))
resources_dir = os.path.join(base_dir, 'resources')

def play_video(video_file):
    """Play video in fullscreen mode."""
    video_path = os.path.join(resources_dir, video_file)
    
    # Open the video file using OpenCV
    cap = cv2.VideoCapture(video_path)
    
    if (cap.isOpened() == False):
        print("Error opening video file")

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            cv2.namedWindow('Mr. Smith', cv2.WINDOW_NORMAL)
            cv2.setWindowProperty('Mr. Smith', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow('Mr. Smith', frame)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    play_video("videos/smith_s2.mp4")

main()