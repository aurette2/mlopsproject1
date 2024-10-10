
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import os
from dotenv import load_dotenv 

from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor

# INDICATION = 'RLL crackles, eval for pneumonia'
INDICATION = 'New basal consolidation, eval for pneumonia; Moderate retrocardiac atelectasis, eval for pneumonia; Mild pulmonary edema, eval for pulmonary congestion; Severe cardiomegaly, eval for heart size; Small pleural effusions, eval for pleural abnormalities; Diffuse nodular parenchymal opacities, eval for possible malignancy; Trace bilateral pleural effusions, eval for effusion; No pneumothorax, eval for pneumothorax; Irregular pleural thickening, eval for tumor involvement; Atelectasis, eval for underlying cause'

class BlipMed:
    def __init__(self) :
        self.processor = BlipProcessor.from_pretrained("nathansutton/generate-cxr")
        self.model = BlipForConditionalGeneration.from_pretrained("nathansutton/generate-cxr")
        self.default_indication = INDICATION
        self.max_lenght = 1024
    
    def generate_report(self, image, my_indication=None):
        
        # process the inputs
        text_input = 'indication: ' + (self.default_indication if my_indication is None else my_indication)
        inputs = self.processor(
            images=image, 
            text=text_input,
            return_tensors="pt"
        )
        
        # generate an entire radiology report
        output = self.model.generate(**inputs,max_length=self.max_lenght)
        report = self.processor.decode(output[0], skip_special_tokens=True, clean_up_tokenization_spaces=False)
        
        return report
    
# if __name__ == "__main__":
#     load_dotenv()
#     IMAGE_BASE_PATH = os.getenv('IMAGE_BASE_PATH')
#     blipMed = BlipMed()

#     if IMAGE_BASE_PATH is None:
#         raise ValueError("The image path (IMAGE_BASE_PATH) is not defined. Check your .env file.")

#     image_path = os.path.join(IMAGE_BASE_PATH, 's50021863.jpg')

#     if not os.path.exists(image_path):
#         raise FileNotFoundError(f"The image {image_path} could not be found.")
    
#     report = blipMed.generate_report(image_path)
#     print(report)
    
    


























