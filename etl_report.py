import os
import pandas as pd
from PIL import Image
import torch
from torchvision import models, transforms
import numpy as np
from dotenv import load_dotenv


from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from alibi_detect.cd import KSDrift, ChiSquareDrift

load_dotenv()
DATA_FOR_DRIFT_PATH=os.getenv("DATA_FOR_DRIFT_PATH")
WINDOWS_SIZE=800

# Pre-trained ResNet for feature extraction
# resnet = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
# resnet = torch.nn.Sequential(*(list(resnet.children())[:-1]))  # Remove the last layer (classification)
# resnet.eval()  # Set the model to evaluation mode

# Define transformation for the images (resize, normalize)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# def extract_features(img_path):
#     img = Image.open(img_path).convert('RGB')
#     img = transform(img).unsqueeze(0)  # Add batch dimension
#     with torch.no_grad():
#         features = resnet(img)
#     return features.squeeze().numpy()  # Convert to numpy array

def extract_rgb_features(img_path):
    # Open the image and convert to RGB
    img = Image.open(img_path).convert('RGB')
    
    # Convert image to a NumPy array
    img_array = np.array(img)
    
    # Calculate the mean for each channel (R, G, B)
    red_mean = np.mean(img_array[:, :, 0])
    green_mean = np.mean(img_array[:, :, 1])
    blue_mean = np.mean(img_array[:, :, 2])
    
    # Return as a NumPy array
    return np.array([red_mean, green_mean, blue_mean])


# Load images and extract features from train and test datasets
def load_images_from_folder(folder, windows_size=WINDOWS_SIZE):
    features = []
    for filename in os.listdir(folder):
        img_path = os.path.join(folder, filename)
        # feature = extract_features(img_path)
        feature = extract_rgb_features(img_path)
        features.append(feature)
    return np.array(features)

X_ref = load_images_from_folder(os.path.join(DATA_FOR_DRIFT_PATH, 'mimic_dset/re_512_3ch/Valid'))  # Path to your train images
X_test = load_images_from_folder(os.path.join(DATA_FOR_DRIFT_PATH, 'mimic_dset/re_512_3ch/Test'))  # Path to your test images


# def generate_drift_report():
    
#     feature_names = ["red_mean", "green_mean", "blue_mean"]
#     X_ref_df = pd.DataFrame(X_ref, columns=feature_names)
#     X_test_df = pd.DataFrame(X_test, columns=feature_names)

#     # Create an Evidently report to monitor data drift
#     report = Report(metrics=[
#         DataDriftPreset(num_stattest="ks", stattest_threshold=0.05),
#         DataQualityPreset()
        
#     ])
    
#     # Fit the report on the reference and test datasets
#     report.run(reference_data=X_ref_df, current_data=X_test_df)

#     # Save the report as HTML
#     report.save_html(os.path.join(DATA_FOR_DRIFT_PATH, 'drift_report.html'))
    
#     return report

# Modify the function to create the Evidently report
def generate_drift_report():
    # Load the datasets and perform drift detection
    reference_path = "Cleanses csv tfrecords/df_train.csv"
    actual_path = "Cleanses csv tfrecords/df_val.csv"
    # length_drift, token_drift, reference_reports, actual_reports = check_columns_and_detect_drift(reference_path, actual_path)

    # Load image datasets
    X_ref = load_images_from_folder(os.path.join(DATA_FOR_DRIFT_PATH, 'mimic_dset/re_512_3ch/Valid'))  # Reference images
    X_test = load_images_from_folder(os.path.join(DATA_FOR_DRIFT_PATH, 'mimic_dset/re_512_3ch/Test'))  # Test images

    # Prepare data for the report
    feature_names = ["red_mean", "green_mean", "blue_mean"]
    X_ref_df = pd.DataFrame(X_ref, columns=feature_names)
    X_test_df = pd.DataFrame(X_test, columns=feature_names)

    # Create an Evidently report
    report = Report(metrics=[
        DataDriftPreset(num_stattest="ks", stattest_threshold=0.05),
        DataQualityPreset()
    ])
    # print(length_drift, token_drift)
    # Run the report on the datasets
    report.run(reference_data=X_ref_df, current_data=X_test_df)

    # Log custom drift results to the report's metadata or save as json modifier le fichier json et reload...
    # report.data['length_drift'] = {
    #     "p_value": length_drift['data']['p_val'],  # P-value for length drift
    #     "is_drift": length_drift['data']['is_drift']  # Drift detection result for length
    # }
    # report.data['token_drift'] = {
    #     "p_value": token_drift['data']['p_val'],  # P-value for token drift
    #     "is_drift": token_drift['data']['is_drift']  # Drift detection result for tokens
    # }

    # Save the report as HTML
    report.save_html(os.path.join(DATA_FOR_DRIFT_PATH, 'drift_report.html'))

    return report


# _________________________________Test data___________________________________#

# Function to check for num_words and token_count, and perform drift detection
def check_columns_and_detect_drift(reference_path, actual_path):
    # Load the datasets
    reference_reports = pd.read_csv(os.path.join(DATA_FOR_DRIFT_PATH, reference_path))
    actual_reports = pd.read_csv(os.path.join(DATA_FOR_DRIFT_PATH, actual_path))

    # Check for num_words column and create if not present
    if "num_words" not in reference_reports.columns:
        reference_reports["num_words"] = reference_reports.text.apply(lambda x: len(x.split(" ")))
    if "num_words" not in actual_reports.columns:
        actual_reports["num_words"] = actual_reports.text.apply(lambda x: len(x.split(" ")))

    # Use the token_count column if it exists, otherwise create it
    if "token_count" not in reference_reports.columns:
        reference_reports["token_count"] = reference_reports["num_words"].apply(
            lambda x: "small" if x <= 100 else ("medium" if x <= 250 else "large")
        )
    if "token_count" not in actual_reports.columns:
        actual_reports["token_count"] = actual_reports["num_words"].apply(
            lambda x: "small" if x <= 100 else ("medium" if x <= 250 else "large")
        )

    # Extracting the arrays for drift detection
    ref_num = np.array(reference_reports["num_words"])
    actual_num = np.array(actual_reports["num_words"])

    ref_token = np.array(reference_reports["token_count"])
    actual_token = np.array(actual_reports["token_count"])

    # Perform KS Drift Detection on word counts
    length_drift_detector = KSDrift(ref_num, p_val=0.05)
    length_drift_result = length_drift_detector.predict(actual_num, return_p_val=True)

    # Perform Chi-Square Drift Detection on token counts
    target_drift_detector = ChiSquareDrift(ref_token, p_val=0.05)
    token_drift_result = target_drift_detector.predict(actual_token, return_p_val=True, return_distance=True)

    return length_drift_result, token_drift_result, reference_reports, actual_reports







