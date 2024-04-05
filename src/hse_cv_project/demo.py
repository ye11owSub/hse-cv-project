import argparse
import time

import cv2

from hse_cv_project.interface import Yolov5Tflite


def detect_video(weights, webcam, img_size, conf_thres, iou_thres):
    start_time = time.time()

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoCapture(webcam)
    fps = video.get(cv2.CAP_PROP_FPS)
    h = int(video.get(3))
    w = int(video.get(4))
    print(w, h)
    result_video_filepath = "webcam_yolov5_output.mp4"
    out = cv2.VideoWriter(result_video_filepath, fourcc, int(fps), (h, w))

    yolov5_tflite_obj = Yolov5Tflite(weights, img_size, conf_thres, iou_thres)

    size = (img_size, img_size)
    while True:
        check, frame = video.read()

        if not check:
            break
        predicted_image = yolov5_tflite_obj.generete_predicted_image(frame, size, w, h)

        out.write(predicted_image)

        cv2.imshow("output", predicted_image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        end_time = time.time()
        print("FPS:", 1 / (end_time - start_time))
        start_time = end_time
    out.release()
    video.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--weights", type=str, default="yolov5s.pt", help="model.pt path(s)")
    parser.add_argument(
        "-vp",
        "--video_path",
        type=str,
        default="share/MOT16 14.mp4",
        help="video path",
    )
    parser.add_argument("--img_size", type=int, default=416, help="image size")  # height, width
    parser.add_argument("--conf_thres", type=float, default=0.25, help="object confidence threshold")
    parser.add_argument("--iou_thres", type=float, default=0.45, help="IOU threshold for NMS")

    opt = parser.parse_args()

    print(opt)
    detect_video(opt.weights, opt.video_path, opt.img_size, opt.conf_thres, opt.iou_thres)
