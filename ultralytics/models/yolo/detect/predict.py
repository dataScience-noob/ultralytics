from datetime import datetime
import csv
from ultralytics.engine.predictor import BasePredictor
from ultralytics.engine.results import Results
from ultralytics.utils import ops

class DetectionPredictor(BasePredictor):
    """
    A class extending the BasePredictor class for prediction based on a detection model.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.detections_file = 'detections.csv'

    def postprocess(self, preds, img, orig_imgs):
        """Post-processes predictions and returns a list of Results objects."""
        preds = ops.non_max_suppression(
            preds,
            self.args.conf,
            self.args.iou,
            agnostic=self.args.agnostic_nms,
            max_det=self.args.max_det,
            classes=self.args.classes,
        )

        if not isinstance(orig_imgs, list):  # input images are a torch.Tensor, not a list
            orig_imgs = ops.convert_torch2numpy_batch(orig_imgs)

        results = []
        for i, pred in enumerate(preds):
            orig_img = orig_imgs[i]
            pred[:, :4] = ops.scale_boxes(img.shape[2:], pred[:, :4], orig_img.shape)
            img_path = self.batch[0][i]
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.detections_file, 'a', newline='') as file:
                writer = csv.writer(file)
                for result in pred:
                    class_name = self.model.names[int(result[5])]
                    writer.writerow([timestamp, class_name])
            results.append(Results(orig_img, path=img_path, names=self.model.names, boxes=pred))
        return results
