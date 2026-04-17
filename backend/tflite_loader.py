"""
TFLite loader for MobileNetV2 food classification.
Calorie lookup uses portion-size heuristic only (no static food DB).
"""

import io
import urllib.request
import numpy as np
from PIL import Image

TFLITE_MODEL_PATH = "mobilenet.tflite"
LABELS_URL        = "https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt"

_interpreter = None
_labels      = None

# Default calories by portion size only
PORTION_CALORIES = {
    'small':  150,
    'medium': 250,
    'large':  450,
}

def _estimate_portion(label):
    label = label.lower()
    large_kw = ['pizza', 'burger', 'hamburger', 'steak', 'chicken', 'roast',
                 'loaf', 'cake', 'doughnut', 'waffle', 'burrito', 'hotdog',
                 'pulled', 'fried', 'hen', 'cock', 'rooster']
    small_kw = ['lemon', 'strawberry', 'mushroom', 'egg', 'espresso',
                 'cauliflower', 'cucumber', 'candy', 'almond', 'walnut', 'peanut']
    for kw in large_kw:
        if kw in label:
            return 'large'
    for kw in small_kw:
        if kw in label:
            return 'small'
    return 'medium'


def _load_labels():
    global _labels
    if _labels is None:
        try:
            with open("imagenet_labels.txt") as f:
                _labels = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print("[TFLite] Downloading ImageNet labels...")
            with urllib.request.urlopen(LABELS_URL) as r:
                _labels = [line.decode().strip() for line in r.readlines()]
            with open("imagenet_labels.txt", "w") as f:
                f.write("\n".join(_labels))
    return _labels


def _load_interpreter():
    global _interpreter
    if _interpreter is None:
        import tflite_runtime.interpreter as tflite
        print("[TFLite] Loading model from", TFLITE_MODEL_PATH)
        _interpreter = tflite.Interpreter(model_path=TFLITE_MODEL_PATH)
        _interpreter.allocate_tensors()
        print("[TFLite] Model ready!")
    return _interpreter


def analyze_food_tflite(image_bytes):
    """
    Run MobileNetV2 TFLite inference.
    Returns (result_dict, error_string).
    """
    try:
        interpreter = _load_interpreter()
        labels      = _load_labels()

        img       = Image.open(io.BytesIO(image_bytes)).convert('RGB').resize((224, 224))
        img_array = np.array(img, dtype=np.float32)
        img_array = (img_array / 127.5) - 1.0
        img_array = np.expand_dims(img_array, axis=0)

        input_details  = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        interpreter.set_tensor(input_details[0]['index'], img_array)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])[0]

        top5_idx = output.argsort()[-5:][::-1]
        top5     = [
            (labels[i] if i < len(labels) else 'unknown', float(output[i]))
            for i in top5_idx
        ]

        best_label_raw = top5[0][0]
        best_score     = top5[0][1]

        food_name   = best_label_raw.replace('_', ' ').title()
        portion     = _estimate_portion(best_label_raw)
        calories    = PORTION_CALORIES[portion]
        confidence  = 'high' if best_score >= 0.6 else 'medium' if best_score >= 0.3 else 'low'
        top3_names  = [t[0].replace('_', ' ').title() for t in top5[:3]]
        description = f"Detected as {top3_names[0]}. Also similar to: {top3_names[1]}, {top3_names[2]}."

        print(f"[TFLite] {food_name} | {round(best_score*100,1)}% | {calories} kcal ({portion})")

        return {
            'food_name':         food_name,
            'calories':          calories,
            'estimated_portion': portion,
            'confidence':        confidence,
            'description':       description,
        }, None

    except Exception as e:
        import traceback
        print(f"[TFLite] ERROR: {e}\n{traceback.format_exc()}")
        return None, str(e)
