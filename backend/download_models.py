import torch
import os
from facenet_pytorch import MTCNN, InceptionResnetV1
import torchvision.models as models
from torchvision.models import MobileNet_V2_Weights

def download_models():
    print("Pre-downloading ML models to bake into Docker image...")
    
    device = torch.device('cpu') # Always download for CPU in build env
    
    # 1. 下载 FaceNet MTCNN
    print("Downloading MTCNN...")
    MTCNN(
        image_size=160, 
        margin=14, 
        min_face_size=20, 
        thresholds=[0.6, 0.7, 0.7], 
        post_process=True,
        device=device
    )
    
    # 2. 下载 InceptionResnetV1
    print("Downloading InceptionResnetV1 (vggface2)...")
    InceptionResnetV1(pretrained='vggface2').eval().to(device)
    
    # 3. 下载 MobileNetV2
    print("Downloading MobileNetV2...")
    models.mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT).eval().to(device)
    
    print("All models downloaded successfully.")

if __name__ == "__main__":
    download_models()
