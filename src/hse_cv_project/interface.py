import cv2
import numpy as np
import tensorflow as tf
from cv2.typing import MatLike
from PIL import Image

from hse_cv_project.utils import letterbox_image, scale_coords

CLASS_NAMES = [
    "person",
    "bicycle",
    "car",
    "motorcycle",
    "airplane",
    "bus",
    "train",
    "truck",
    "boat",
    "traffic light",
    "fire hydrant",
    "stop sign",
    "parking meter",
    "bench",
    "bird",
    "cat",
    "dog",
    "horse",
    "sheep",
    "cow",
    "elephant",
    "bear",
    "zebra",
    "giraffe",
    "backpack",
    "umbrella",
    "handbag",
    "tie",
    "suitcase",
    "frisbee",
    "skis",
    "snowboard",
    "sports ball",
    "kite",
    "baseball bat",
    "baseball glove",
    "skateboard",
    "surfboard",
    "tennis racket",
    "bottle",
    "wine glass",
    "cup",
    "fork",
    "knife",
    "spoon",
    "bowl",
    "banana",
    "apple",
    "sandwich",
    "orange",
    "broccoli",
    "carrot",
    "hot dog",
    "pizza",
    "donut",
    "cake",
    "chair",
    "couch",
    "potted plant",
    "bed",
    "dining table",
    "toilet",
    "tv",
    "laptop",
    "mouse",
    "remote",
    "keyboard",
    "cell phone",
    "microwave",
    "oven",
    "toaster",
    "sink",
    "refrigerator",
    "book",
    "clock",
    "vase",
    "scissors",
    "teddy bear",
    "hair drier",
    "toothbrush",
]


class Yolov5Tflite:
    def __init__(
        self,
        weights="yolov5s-fp16.tflite",
        image_size=416,
        conf_thres=0.25,
        iou_thres=0.45,
    ):
        self.weights = weights
        self.image_size = image_size
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres

        self.names = CLASS_NAMES

    def xywh2xyxy(self, x):
        # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
        y = x.copy()
        y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
        y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
        y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
        y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
        return y

    def non_max_suppression(self, boxes, scores, threshold):
        assert boxes.shape[0] == scores.shape[0]
        # bottom-left origin
        ys1 = boxes[:, 0]
        xs1 = boxes[:, 1]
        # top-right target
        ys2 = boxes[:, 2]
        xs2 = boxes[:, 3]
        # box coordinate ranges are inclusive-inclusive
        areas = (ys2 - ys1) * (xs2 - xs1)
        scores_indexes = scores.argsort().tolist()
        boxes_keep_index = []
        while len(scores_indexes):
            index = scores_indexes.pop()
            boxes_keep_index.append(index)
            if not len(scores_indexes):
                break
            ious = self.compute_iou(boxes[index], boxes[scores_indexes], areas[index], areas[scores_indexes])
            filtered_indexes = set((ious > threshold).nonzero()[0])
            # if there are no more scores_index
            # then we should pop it
            scores_indexes = [v for (i, v) in enumerate(scores_indexes) if i not in filtered_indexes]
        return np.array(boxes_keep_index)

    def compute_iou(self, box, boxes, box_area, boxes_area):
        # this is the iou of the box against all other boxes
        assert boxes.shape[0] == boxes_area.shape[0]
        # get all the origin-ys
        # push up all the lower origin-xs, while keeping the higher origin-xs
        ys1 = np.maximum(box[0], boxes[:, 0])
        # get all the origin-xs
        # push right all the lower origin-xs, while keeping higher origin-xs
        xs1 = np.maximum(box[1], boxes[:, 1])
        # get all the target-ys
        # pull down all the higher target-ys, while keeping lower origin-ys
        ys2 = np.minimum(box[2], boxes[:, 2])
        # get all the target-xs
        # pull left all the higher target-xs, while keeping lower target-xs
        xs2 = np.minimum(box[3], boxes[:, 3])
        # each intersection area is calculated by the
        # pulled target-x minus the pushed origin-x
        # multiplying
        # pulled target-y minus the pushed origin-y
        # we ignore areas where the intersection side would be negative
        # this is done by using maxing the side length by 0
        intersections = np.maximum(ys2 - ys1, 0) * np.maximum(xs2 - xs1, 0)
        # each union is then the box area
        # added to each other box area minusing their intersection calculated above
        unions = box_area + boxes_area - intersections
        # element wise division
        # if the intersection is 0, then their ratio is 0
        ious = intersections / unions
        return ious

    def nms(self, prediction):
        prediction = prediction[prediction[..., 4] > self.conf_thres]

        # Box (center x, center y, width, height) to (x1, y1, x2, y2)
        boxes = self.xywh2xyxy(prediction[:, :4])

        res = self.non_max_suppression(boxes, prediction[:, 4], self.iou_thres)

        result_boxes = []
        result_scores = []
        result_class_names = []
        for r in res:
            result_boxes.append(boxes[r])
            result_scores.append(prediction[r, 4])
            result_class_names.append(self.names[np.argmax(prediction[r, 5:])])

        return result_boxes, result_scores, result_class_names

    def detect(self, image):
        original_size = image.shape[:2]
        input_data = np.ndarray(shape=(1, self.image_size, self.image_size, 3), dtype=np.float32)
        # image = cv2.resize(image,(self.image_size,self.image_size))
        # input_data[0] = image.astype(np.float32)/255.0
        input_data[0] = image
        interpreter = tf.lite.Interpreter(self.weights)
        interpreter.allocate_tensors()

        # Get input and output tensors
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        interpreter.set_tensor(input_details[0]["index"], input_data)
        interpreter.invoke()
        pred = interpreter.get_tensor(output_details[0]["index"])

        # Denormalize xywh
        pred[..., 0] *= original_size[1]  # x
        pred[..., 1] *= original_size[0]  # y
        pred[..., 2] *= original_size[1]  # w
        pred[..., 3] *= original_size[0]  # h

        result_boxes, result_scores, result_class_names = self.nms(pred)

        return result_boxes, result_scores, result_class_names

    def generete_predicted_image(self, image: MatLike, size: tuple[int, int], width: int, height: int) -> MatLike:
        image_resized = letterbox_image(Image.fromarray(image), size)
        image_array = np.asarray(image_resized)

        normalized_image_array = image_array.astype(np.float32) / 255.0
        result_boxes, result_scores, result_class_names = self.detect(normalized_image_array)

        if len(result_boxes) > 0:
            result_boxes = scale_coords(size, np.array(result_boxes), (width, height))
            font = cv2.FONT_HERSHEY_SIMPLEX

            # org
            org = (20, 40)

            # fontScale
            fontScale = 0.5

            # Blue color in BGR
            color = (0, 255, 0)

            # Line thickness of 1 px
            thickness = 1

            for i, r in enumerate(result_boxes):
                org = (int(r[0]), int(r[1]))
                cv2.rectangle(
                    image,
                    (int(r[0]), int(r[1])),
                    (int(r[2]), int(r[3])),
                    (255, 0, 0),
                    1,
                )
                cv2.putText(
                    image,
                    str(int(100 * result_scores[i])) + "%  " + str(result_class_names[i]),
                    org,
                    font,
                    fontScale,
                    color,
                    thickness,
                    cv2.LINE_AA,
                )

        return image
