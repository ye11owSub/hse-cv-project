import os

import cv2
import streamlit as st

from hse_cv_project.interface import Yolov5Tflite


def run_video(weights, video_path, img_size, conf_thres, iou_thres):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)

    video_name = "webcam_yolov5_output.mp4"
    outputpath = os.path.join("data/video_output", video_name)
    os.makedirs("data/video_frames", exist_ok=True)

    h = int(video.get(3))
    w = int(video.get(4))
    size = (img_size, img_size)
    out = cv2.VideoWriter(outputpath, fourcc, int(fps), (h, w))

    vdo_view = st.empty()
    warning = st.empty()

    yolov5_tflite_obj = Yolov5Tflite(weights, img_size, conf_thres, iou_thres)

    with st.spinner(text="Predicting..."):
        warning.warning(
            "This is realtime prediction, If you wish to download the final prediction result wait until the process done.",
            icon="⚠️",
        )
        while True:
            ret, frame = video.read()
            if not ret:
                break
            predicted_image = yolov5_tflite_obj.generete_predicted_image(frame, size, w, h)

            vdo_view.image(predicted_image, caption="Current Model Prediction(s)")
            out.write(predicted_image)
        out.release()
        video.release()

    # Display Video
    output_video = open(outputpath, "rb")
    output_video_bytes = output_video.read()
    st.video(output_video_bytes)
    st.write("Model Prediction")
    vdo_view.empty()


def main():
    st.header("📦 YOLOv5 Streamlit Deployment Example")
    st.sidebar.markdown("https://github.com/ye11owSub/hse-cv-project")

    submit = st.button("Predict!")
    if submit:
        run_video("share/model_float16_quant.tflite", "share/MOT16 14.mp4", 416, 0.25, 0.45)


if __name__ == "__main__":
    main()
