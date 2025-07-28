from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import fitz 
import os
import io
from models import ChatConversation
from extensions import db
from werkzeug.utils import secure_filename
import requests as rq
import ollama

class CancerAnalysisService:
    def __init__(self, app=None):
        self.app = app
        self.lung_model = None
        self.brain_model = None
        self.uploads_dir = None
        
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.uploads_dir = os.path.join(app.instance_path, 'uploads')
        os.makedirs(self.uploads_dir, exist_ok=True)

        model_dir = app.config.get('MODEL_DIR', 'models')
        self.lung_model = load_model(os.path.join(model_dir, 'lung_model.h5'))
        self.brain_model = load_model(os.path.join(model_dir, 'brain_model.h5'))
        app.logger.info(f"Lung model input shape: {self.lung_model.input_shape}")
        app.logger.info(f"Brain model input shape: {self.brain_model.input_shape}")


    def analyze_image(self, image_file, patient_id, doctor_id):
        temp_path = None
        
        try:
            filename = secure_filename(image_file.filename)
            temp_path = os.path.join(self.uploads_dir, filename)
            image_file.save(temp_path)
            
            # Process the image
            img = Image.open(temp_path)
            image_type = self._detect_image_type(img, filename)
            
            result = self._analyze_with_model(img, image_type)
            
            # Clean up
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            
            return {
                'patient_id': patient_id,
                'analysis_type': f"{image_type.title()} Cancer Detection",
                'result': result['result'],
                'confidence_score': result['confidence'],
                'risk_level': result['risk_level'],
                'recommendations': result['recommendations'],
                'image_filename': filename,
                'image_type': image_type,
                'analyzed_by': doctor_id
            }
            
        except Exception as e:
            # Clean up if error occurs
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            raise e

    def _detect_image_type(self, img, filename):
        filename_lower = filename.lower()
        
        if 'lung' in filename_lower or 'chest' in filename_lower:
            return 'lung'
        if 'brain' in filename_lower or 'mri' in filename_lower:
            return 'brain'
        
        raise ValueError("Could not determine image type")

    def _analyze_with_model(self, img, image_type):
        model = self.lung_model if image_type == 'lung' else self.brain_model
        img_array = self._preprocess_image(img, image_type)
        prediction = model.predict(np.expand_dims(img_array, axis=0))
        return self._interpret_prediction(prediction, image_type)

    def _preprocess_image(self, img, image_type):
        # Convert to RGB if grayscale (1 channel)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize based on model requirements
        target_size = (128, 128)  # Adjust based on your model's expected input size
        img = img.resize(target_size)
        
        # Convert to numpy array and normalize
        img_array = np.array(img) / 255.0
        
        # Ensure proper shape (height, width, channels)
        if len(img_array.shape) == 2:  # If grayscale somehow
            img_array = np.stack((img_array,)*3, axis=-1)  # Convert to 3 channels
        
        return img_array

    def _interpret_prediction(self, prediction, image_type):
        confidence = float(prediction[0][0])
        
        if image_type == 'lung':
            result = ('Potential lung malignancy' if confidence > 0.8
                     else 'No signs of lung cancer')
            specialist = 'pulmonologist'
        else:
            result = ('Potential brain tumor' if confidence > 0.8
                     else 'No signs of brain tumor')
            specialist = 'neurologist'
        
        risk_level = ('high' if confidence > 0.8 else
                     'medium' if confidence > 0.5 else
                     'low')
        
        return {
            'result': result,
            'confidence': confidence,
            'risk_level': risk_level
        }
class ChatbotService:
    def __init__(self):
        self.uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        os.makedirs(self.uploads_dir, exist_ok=True)

    def extract_file(self, file):
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(self.uploads_dir, filename)
            file.save(file_path)
            return file_path
        return None
    
    def extract_text_from_pdf(self, file_path):
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            return None
    
    def fetch_history(self, user_id):
        conversations = ChatConversation.query.filter_by(user_id=user_id).order_by(ChatConversation.created_at.desc()).all()
        return [{'role': conv.role, 'content': conv.content, 'is_file': conv.is_file, 'file_name': conv.file_name} for conv in conversations]

    def get_file_content(self, file_path):
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return f.read()
        return None
    
    def get_response(self, user_message, user_id, role='user',is_file=False, file_name=None):
        messages= [{'role': 'system', 'content': 'You are a helpful medical assistant.'}]
        if is_file and file_name:
            filename = file_name.filename  # extract the name
            file_path = self.extract_file(file_name)
            if not file_path:
                return "File upload failed."

            if filename.lower().endswith('.pdf'):
                content = self.extract_text_from_pdf(file_path)
                #write the content to a file
                if content is None:
                    return "Failed to extract text from PDF."  
                with open(os.path.join(self.uploads_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(content)

            else:
                raw = self.get_file_content(file_path)
                content = raw.decode('utf-8') if raw else None

            if not content:
                return "Failed to read or extract content from the file."

            messages.append({
                'role': role,
                'content': content,
                'is_file': True,
                'file_name': filename
            })

            self.save_conversation(user_id, role, content, is_file=True, file_name=filename)
        else:
            self.save_conversation(user_id, role, user_message)
            messages.append({
                'role': role,
                'content': user_message,
                'is_file': False
            })
        try:
            messages = [{'role': msg['role'], 'content': msg['content']} for msg in messages]
            response = ollama.chat(
                    model="monotykamary/medichat-llama3:8b",
                    messages= messages,
                    stream=False
                )
            assistant_message = response['message']['content']

            self.save_conversation(user_id, 'assistant', assistant_message)
            
            return assistant_message
        
        except Exception as e:
            return f"Error: {str(e)}"

    def save_conversation(self, user_id, role, content, is_file=False, file_name=None):
        conversation = ChatConversation(
            user_id=user_id,
            role=role,
            content=content,
            is_file=is_file,
            file_name=file_name
        )
        db.session.add(conversation)
        db.session.commit()
        return conversation
    
cancer_service = CancerAnalysisService()
chatbot_service = ChatbotService()