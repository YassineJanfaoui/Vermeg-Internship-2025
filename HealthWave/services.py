from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import os
import io
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
        
        recommendations = (
            f'Immediate {specialist} consultation' if risk_level == 'high' else
            'Follow-up imaging recommended' if risk_level == 'medium' else
            'Continue regular screening'
        )
        
        return {
            'result': result,
            'confidence': confidence,
            'risk_level': risk_level,
            'recommendations': recommendations
        }
class ChatbotService:
    def __init__(self):
        self.uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        os.makedirs(self.uploads_dir, exist_ok=True)

    def get_response(self, conversation_history, file=None):
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(self.uploads_dir, filename)
            file.save(filepath)
            
            try:
                text_content = self._extract_text_from_file(filepath)
                conversation_history[-1]['content'] += f"\n[Attached file content]:\n{text_content}"
            except Exception as e:
                raise ValueError(f"Could not process file: {str(e)}")
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        response = ollama.chat(
            model="medllama2:7b",
            messages=conversation_history
        )
        return response['message']['content']
    
    def _extract_text_from_file(self, filepath):
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()
        
        if ext == '.pdf':
            return self._extract_text_from_pdf(filepath)
        elif ext in ('.doc', '.docx'):
            return self._extract_text_from_word(filepath)
        elif ext == '.txt':
            with open(filepath, 'r') as f:
                return f.read()
        else:
            raise ValueError("Unsupported file type")

    def _extract_text_from_pdf(self, filepath):
        try:
            import PyPDF2
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = "\n".join([page.extract_text() for page in reader.pages])
                return text
        except ImportError:
            raise ValueError("PDF processing requires PyPDF2 package")

    def _extract_text_from_word(self, filepath):
        try:
            from docx import Document
            doc = Document(filepath)
            return "\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            raise ValueError("Word processing requires python-docx package")
        
    def save_conversation(self, user_id, role, content, is_file=False, file_name=None):
        from models import ChatConversation, db
        try:
            message = ChatConversation(
                user_id=user_id,
                role=role,
                content=content,
                is_file=is_file,
                file_name=file_name
            )
            db.session.add(message)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_conversation_history(self, user_id, limit=20):
        from models import ChatConversation
        return ChatConversation.query.filter_by(user_id=user_id)\
                                   .order_by(ChatConversation.created_at.desc())\
                                   .limit(limit)\
                                   .all()
    
cancer_service = CancerAnalysisService()
chatbot_service = ChatbotService()