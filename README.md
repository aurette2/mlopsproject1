# Image-to-Text ( Report for Image Chess X-Ray )

 Product An AI-powered image-to-text system that automates the generation of Chest X-ray (CXR) diagnostic reports and provides visual question answering (VQA) for specific clinical questions based on CXR images. The system will integrate with existing healthcare infrastructure and be accessible via API for authorised staff.

# Project structure 

- `backend/app/`:Contains the `modelblip.py` file in which we have defined a class to download our pretrained model and make prediction, `etl_report.py` contains the implementation of drift detection using evidently on Chess X-ray images, `controller.py` contains our APIs served by fastapi.
- `dataops`: This folder contains all the data manipulated in the system (input data, output, temporal) and tracked using dvc.
- `frontend`: This folder contains the file `app.py` in which there is the implementation of all the user interfaces. 
- `Dockerfile`: This file contains all the commands we requires to call on the command line to assemble an image.
- `main.py`: Contains the workflow needed to perform the of our model (command line prediction)  with specific . 
- `requirements.txt`: Contains the specific packages to install for the project to function properly



# Setup

### Clone

```bash
  git clone https://github.com/aurette2/mlopsproject1group3.git
```
```
cd mlopsproject1group3/project1
```
### Install requirements
- Create an activate a virtual enviroment
```
    pip install virtualenv
    virtualenv venv
    source venv/bin/activate
```

```
pip install -r requirements.txt
```

### Run it locally 
launch the backend (fastapi)
```bash
   cd backend/app

   fastapi run main.py
```
launch the streamlit ()
```bash
   cd frontend

   streamlit run app.y
```

### Run it locally in docker image

```
    cd mlopsproject1group3/project2
```

```
    docker build -t fastapi-project:latest .
```

```
    docker run -d -p 8000 -p 8501 fastapi-project:latest 
```

# Tech Stack

- **Frontend:** Streamlit
- **Backend:** Fastapi, 
- **Data Management:** DVC, Git
- **CI/CD Pipeline:** Github action 
- **Deployment:** Azure, 
- **Orchestration:**  Apache airflow,
- **Monitoring:** Evidently AI 


# Appendix
Aditionals guide and Assets that can help to better understand this project.
- [Google Drive link of projects artefacts](https://drive.google.com/drive/folders/1rI5kliXcn50TZAS0ZsWDgl56ZBZz_Nv2?usp=sharing)
- [ generate-cxr ](https://huggingface.co/nathansutton/generate-cxr)



## License

[MIT](https://choosealicense.com/licenses/mit/)

------------------------------------------------------------------------------------------------------------

⭐️ If you find this repository helpful, we’d be thrilled if you could give it a star! 
