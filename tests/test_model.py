import pytest
from unittest.mock import patch, MagicMock
from PIL import Image
from model import BlipMed

# Initialize the BlipMed instance for testing
blip_med = BlipMed()

@pytest.fixture
def sample_image():
    # Create a small sample image for testing
    image = Image.new('RGB', (128, 128), color = 'white')
    return image

@patch("model.BlipProcessor")
@patch("model.BlipForConditionalGeneration")
def test_generate_report(mock_model, mock_processor, sample_image):
    # Mock the processor's return values
    mock_processor_instance = MagicMock()
    mock_processor.from_pretrained.return_value = mock_processor_instance
    mock_processor_instance.return_tensors.return_value = {"pixel_values": [[1.0]]}

    # Mock the model's generate method
    mock_model_instance = MagicMock()
    mock_model.from_pretrained.return_value = mock_model_instance
    mock_model_instance.generate.return_value = ["mocked_generated_text"]

    # Mock the processor's decode method
    mock_processor_instance.decode.return_value = "Mocked radiology report"

    # Run the generate_report method
    result = blip_med.generate_report(sample_image, my_indication="test indication")
    
    # Check if the output matches the mocked report
    assert result == "Mocked radiology report"
    mock_model_instance.generate.assert_called_once()

@patch("model.BlipProcessor")
@patch("model.BlipForConditionalGeneration")
def test_generate_report_no_indication(mock_model, mock_processor, sample_image):
    # Mock the processor's return values
    mock_processor_instance = MagicMock()
    mock_processor.from_pretrained.return_value = mock_processor_instance
    mock_processor_instance.return_tensors.return_value = {"pixel_values": [[1.0]]}

    # Mock the model's generate method
    mock_model_instance = MagicMock()
    mock_model.from_pretrained.return_value = mock_model_instance
    mock_model_instance.generate.return_value = ["mocked_generated_text"]

    # Mock the processor's decode method
    mock_processor_instance.decode.return_value = "Mocked radiology report without indication"

    # Run the generate_report method without specifying an indication
    result = blip_med.generate_report(sample_image)
    
    # Check if the output matches the mocked report
    assert result == "Mocked radiology report without indication"
    mock_model_instance.generate.assert_called_once()