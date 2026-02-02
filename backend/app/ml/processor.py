import torch
import torch.nn as nn
import torchvision.transforms as transforms
import cv2
from pathlib import Path

labels = ["Down", "Left", "Nothing", "Right", "Up"]

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model_test_x3d_m_back_epoche4.pb"

model = torch.hub.load("facebookresearch/pytorchvideo", model="x3d_m")
model.blocks[5].proj = nn.Linear(model.blocks[5].proj.in_features, 5)
model.load_state_dict(
    torch.load(
        MODEL_PATH,
        weights_only=True,
        map_location=torch.device("cpu"),
    )
)
model.eval()

transform = transforms.Compose(
    [
        transforms.ToPILImage(),
        transforms.ToTensor(),
        transforms.Resize((224, 224)),
        transforms.Normalize(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225]),
    ]
)


def process_video(video_path: str):
    cap = cv2.VideoCapture(video_path)
    batch_frames = []
    batch_size = 30
    result = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        input_tensor12 = transform(frame).unsqueeze(0)
        input_tensor = torch.permute(input_tensor12, (1, 0, 2, 3))
        batch_frames.append(input_tensor)

        if len(batch_frames) == batch_size:
            input_batch = torch.cat(batch_frames, dim=1)
            input_variable = input_batch.unsqueeze(dim=0)
            with torch.no_grad():
                output = model(input_variable)
            averaged_output = torch.mean(output, dim=0)
            _, predicted_class = torch.max(averaged_output.data, 0)

            batch_frames = []
            result = {
                label: float(value)
                for label, value in zip(labels, averaged_output.data.numpy())
            }

    cap.release()
    return result or {label: 0 for label in labels}
