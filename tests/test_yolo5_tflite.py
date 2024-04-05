import numpy as np
import pytest

from hse_cv_project.interface import Yolov5Tflite


@pytest.fixture
def yolov5_model():
    return Yolov5Tflite(weights="share/model_float16_quant.tflite")


def test_xywh2xyxy(yolov5_model):
    input_boxes = np.array([[10, 10, 20, 20]])  # centerX, centerY, width, height
    expected = np.array([[0, 0, 20, 20]])  # x1, y1, x2, y2
    converted = yolov5_model.xywh2xyxy(input_boxes)
    np.testing.assert_array_equal(converted, expected)


def test_non_max_suppression_single_box(yolov5_model):
    boxes = np.array([[10, 10, 20, 20]])  # x1, y1, x2, y2
    scores = np.array([0.9])
    threshold = 0.4
    kept_indices = yolov5_model.non_max_suppression(boxes, scores, threshold)
    assert len(kept_indices) == 1 and kept_indices[0] == 0


def test_compute_iou(yolov5_model):
    box_a = np.array([0, 0, 10, 10])
    box_b = np.array([[0, 0, 10, 10], [10, 10, 20, 20]])
    expected_iou = np.array([1.0, 0.0])
    iou_values = yolov5_model.compute_iou(box_a, box_b, 100, np.array([100, 100]))
    np.testing.assert_array_almost_equal(iou_values, expected_iou, decimal=2)


def test_detect_shape_and_content(yolov5_model):
    # Assuming a mock image of shape (416, 416, 3) is being passed
    mock_image = np.random.rand(416, 416, 3).astype(np.float32)
    boxes, scores, class_names = yolov5_model.detect(mock_image)
    # Test the expected shapes and content type of returned values
    assert isinstance(boxes, list)
    assert isinstance(scores, list)
    assert isinstance(class_names, list)
    if len(boxes) > 0:  # If there are detections
        assert isinstance(boxes[0], np.ndarray)
        assert isinstance(scores[0], np.float32)
        assert isinstance(class_names[0], str)
