from flask import Flask, render_template, request, url_for, send_file, flash, redirect, make_response, jsonify
import pickle
import numpy as np
import os
import json
import smtplib
from dotenv import load_dotenv
import requests

try:
    import termcolor
except ImportError:
    termcolor = None

try:
    import openai
except ImportError:
    openai = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import tensorflow as tf
except ImportError:
    tf = None

load_dotenv()

if openai:
    openai.api_key = os.getenv("OPENAI_API_KEY")

OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:7b"

messages = []
messages.append({"role": "system", "content": "You are an AI healthcare assistant which greets people as an advanced healthcare assistant and diagnose symptoms to identify disease and provide consultation besides this if something is asked you would say you're a personal AI healthcare assistant and could not discuss any other topic than healthcare and medical"})

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12)

from datetime import datetime
app.jinja_env.globals['now'] = datetime.now

from translations import get_translation

@app.context_processor
def inject_lang():
    lang = request.cookies.get('lang', 'en')
    return {'t': get_translation(lang), 'current_lang': lang}

@app.route('/set-language/<lang>')
def set_language(lang):
    if lang not in ('en', 'hi', 'mr'):
        lang = 'en'
    resp = make_response(redirect(request.referrer or url_for('home')))
    resp.set_cookie('lang', lang, max_age=365*24*3600, path='/', samesite='Lax')
    return resp


def load_legacy_h5(path):
    import h5py
    f = h5py.File(path, 'r')
    config = json.loads(f.attrs.get('model_config'))
    layers_config = config['config']['layers']
    batch_shape = layers_config[0]['config'].get('batch_input_shape')
    input_shape = tuple(batch_shape[1:])

    model = tf.keras.Sequential()
    model.add(tf.keras.layers.InputLayer(shape=input_shape))

    for i, layer_cfg in enumerate(layers_config):
        cls_name = layer_cfg['class_name']
        cfg = dict(layer_cfg['config'])
        if cls_name == 'BatchNormalization' and isinstance(cfg.get('axis'), list):
            cfg['axis'] = cfg['axis'][0]
        if i == 0:
            cfg.pop('batch_input_shape', None)
        layer_cls = getattr(tf.keras.layers, cls_name)
        model.add(layer_cls.from_config(cfg))

    model.load_weights(path)
    f.close()
    return model


def load_models():
    models = {}
    try:
        model_dir = os.path.join(os.path.dirname(__file__), 'models')
        print(f"Loading models from: {model_dir}")

        models['diabetes'] = pickle.load(open(os.path.join(model_dir, 'diabetes.pkl'), 'rb'))
        models['cancer'] = pickle.load(open(os.path.join(model_dir, 'cancer.pkl'), 'rb'))
        models['heart'] = pickle.load(open(os.path.join(model_dir, 'heart.pkl'), 'rb'))
        models['kidney'] = pickle.load(open(os.path.join(model_dir, 'kidney.pkl'), 'rb'))
        models['liver'] = pickle.load(open(os.path.join(model_dir, 'liver.pkl'), 'rb'))

        try:
            models['malaria'] = load_legacy_h5(os.path.join(model_dir, 'malaria.h5'))
        except Exception as e:
            print(f"Error loading malaria model: {str(e)[:100]}")

        try:
            models['pneumonia'] = load_legacy_h5(os.path.join(model_dir, 'pneumonia.h5'))
        except Exception as e:
            print(f"Error loading pneumonia model: {str(e)[:100]}")

        print(f"Models loaded ({len(models)}/7): {list(models.keys())}")

    except Exception as e:
        print(f"Error loading models: {e}")
        import traceback
        print(traceback.format_exc())
    return models


try:
    ML_MODELS = load_models()
except Exception as e:
    print(f"Error loading models: {e}")
    ML_MODELS = {}


def predict(values, disease_type):
    try:
        values = np.asarray(values)
        model = ML_MODELS.get(disease_type)
        if model is None:
            return None, 0

        if hasattr(model, 'predict_proba'):
            pred_proba = model.predict_proba(values.reshape(1, -1))[0]
            pred = model.predict(values.reshape(1, -1))[0]
            predicted_label = pred
            classes = getattr(model, 'classes_', None)
            if classes is not None:
                try:
                    predicted_idx = list(classes).index(predicted_label)
                    confidence = round(float(pred_proba[predicted_idx]) * 100, 2)
                except Exception:
                    confidence = round(float(np.max(pred_proba)) * 100, 2)
            else:
                confidence = round(float(np.max(pred_proba)) * 100, 2)
        else:
            pred = model.predict(values.reshape(1, -1))[0]
            confidence = 100
        return pred, confidence
    except Exception as e:
        print(f"Prediction error: {e}")
        return None, 0


@app.route("/")
@app.route("/home")
def home():
    from flask_login import current_user
    if current_user.is_authenticated:
        from models import DiseasePrediction
        recent = DiseasePrediction.query.filter_by(user_id=current_user.user_id).order_by(
            DiseasePrediction.prediction_date.desc()).limit(3).all()
        return render_template('user/user_home.html', recent_predictions=recent)
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/predictors")
def predictors_page():
    return render_template('predictors.html')

@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        try:
            contactDict = request.form
            firstname = contactDict['firstname']
            lastname = contactDict['lastname']
            email = contactDict['email']
            phone = contactDict['phone']
            description = contactDict['description']

            subject = "Medical Website feedback !!"
            message = f"First Name : {firstname} \nLast Name : {lastname} \nEmail : {email}\nPhone Number : {phone}\nDescription : {description}\n"
            content = f"Subject : {subject} \n\n{message}"

            sender = os.getenv("EMAIL_SENDER")
            receiver = os.getenv("EMAIL_RECEIVER")
            password = os.getenv("EMAIL_PASSWORD")

            if sender and receiver and password:
                with smtplib.SMTP("smtp.gmail.com", 587) as mail:
                    mail.ehlo()
                    mail.starttls()
                    mail.login(sender, password)
                    mail.ehlo()
                    mail.sendmail(sender, receiver, content)
                flash("Message sent successfully!", "success")
            else:
                flash("Email configuration not set", "error")
        except Exception as e:
            flash(f"Error sending message: {str(e)}", "error")

    return render_template("contact.html")

@app.route("/HealthCareAssistant", methods=["POST", "GET"])
def healthcare_assistant():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')

        if not message:
            return jsonify({'reply': 'Please provide a message.'})

        context = ""
        for msg in messages[-6:]:
            if msg["role"] == "system":
                context += f"System: {msg['content']}\n"
            elif msg["role"] == "user":
                context += f"User: {msg['content']}\n"
            else:
                context += f"Assistant: {msg['content']}\n"

        context += f"User: {message}\nAssistant:"
        messages.append({"role": "user", "content": message})

        try:
            response = requests.post(
                OLLAMA_API_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": context,
                    "stream": False,
                    "temperature": 0.7
                },
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                reply = result.get('response', 'Unable to generate response.').strip()
            else:
                reply = "Error connecting to Ollama. Make sure Ollama server is running on http://localhost:11434"

        except requests.exceptions.ConnectionError:
            reply = "Ollama server is not running. Please start it with: ollama serve"
        except Exception as e:
            reply = f"Error: {str(e)}"

        import re
        reply = re.sub(r'#{1,4}\s*(.+)', r'<strong>\1</strong>', reply)
        reply = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', reply)
        reply = re.sub(r'\*(.+?)\*', r'<em>\1</em>', reply)
        reply = re.sub(r'(\d+)\.\s+', r'<br>• ', reply)
        reply = re.sub(r'\n\s*-\s+', r'<br>• ', reply)
        reply = reply.replace('\n\n', '<br><br>')
        reply = reply.replace('\n', '<br>')

        messages.append({"role": "assistant", "content": reply})
        return jsonify({'reply': reply})

    except Exception as e:
        return jsonify({'reply': 'Sorry, I encountered an error. Please try again.'})


@app.route("/diabetes")
def diabetesPage():
    return render_template('diabetes.html')

@app.route("/cancer")
def cancerPage():
    return render_template('cancer.html')

@app.route("/heart")
def heartPage():
    return render_template('heart.html')

@app.route("/kidney")
def kidneyPage():
    return render_template('kidney.html')

@app.route("/liver")
def liverPage():
    return render_template('liver.html')

@app.route("/malaria")
def malariaPage():
    return render_template('malaria.html')

@app.route("/pneumonia")
def pneumoniaPage():
    return render_template('pneumonia.html')

@app.route("/predict", methods=['POST'])
def predict_disease():
    disease_type = None
    try:
        if request.method == 'POST':
            form_data = request.form.to_dict()
            disease_type = form_data.pop('disease_type', None)

            if not disease_type:
                raise ValueError("Disease type not specified")

            if disease_type not in ML_MODELS:
                raise ValueError(f"Model for {disease_type} not loaded. Available models: {list(ML_MODELS.keys())}")

            if disease_type in ['malaria', 'pneumonia']:
                if Image is None or tf is None:
                    raise ValueError("Image processing libraries not available")

                file = request.files.get('image')
                if not file or file.filename == '':
                    raise ValueError("Please upload an image")

                img = Image.open(file.stream)

                if disease_type == 'malaria':
                    img = img.convert('RGB').resize((36, 36))
                    img_array = np.array(img) / 255.0
                else:
                    img = img.convert('L').resize((36, 36))
                    img_array = np.array(img) / 255.0
                    img_array = img_array.reshape(36, 36, 1)

                img_array = np.expand_dims(img_array, axis=0).astype(np.float32)
                model = ML_MODELS[disease_type]
                pred_output = model.predict(img_array, verbose=0)

                if pred_output.shape[-1] == 2:
                    prediction = int(np.argmax(pred_output[0]))
                    confidence = round(float(np.max(pred_output[0])) * 100, 2)
                else:
                    pred_prob = float(pred_output[0][0])
                    prediction = 1 if pred_prob > 0.5 else 0
                    confidence = round(pred_prob * 100 if prediction == 1 else (1 - pred_prob) * 100, 2)

                return render_template(
                    'predict.html',
                    pred=prediction,
                    confidence=confidence,
                    disease_type=disease_type,
                    form_data={'image': file.filename}
                )

            model = ML_MODELS[disease_type]
            model_features = list(getattr(model, 'feature_names_in_', []))

            FIELD_MAPPINGS = {
                'diabetes': {
                    'pregnancies': 'Pregnancies',
                    'glucose': 'Glucose',
                    'bloodpressure': 'BloodPressure',
                    'skinthickness': 'SkinThickness',
                    'insulin': 'Insulin',
                    'bmi': 'BMI',
                    'dpf': 'DiabetesPedigreeFunction',
                    'age': 'Age',
                },
                'cancer': {
                    'concave_points_mean': 'concave points_mean',
                    'concave_points_se': 'concave points_se',
                    'concave_points_worst': 'concave points_worst',
                },
                'liver': {
                    'age': 'Age',
                    'total_bilirubin': 'Total_Bilirubin',
                    'direct_bilirubin': 'Direct_Bilirubin',
                    'alkaline_phosphotase': 'Alkaline_Phosphotase',
                    'alamine_aminotransferase': 'Alamine_Aminotransferase',
                    'aspartate_aminotransferase': 'Aspartate_Aminotransferase',
                    'total_proteins': 'Total_Protiens',
                    'albumin': 'Albumin',
                    'albumin_and_globulin_ratio': 'Albumin_and_Globulin_Ratio',
                    'gender': 'Gender_Male',
                },
            }

            field_map = FIELD_MAPPINGS.get(disease_type, {})
            reverse_map = {v: k for k, v in field_map.items()}

            values = []
            missing = []
            for mf in model_features:
                if mf in form_data:
                    values.append(float(form_data[mf]))
                elif mf in reverse_map and reverse_map[mf] in form_data:
                    values.append(float(form_data[reverse_map[mf]]))
                else:
                    missing.append(mf)

            if missing:
                raise ValueError(f"{disease_type.capitalize()} model inputs missing: {missing}")

            prediction, confidence = predict(values, disease_type)

            if prediction is None:
                raise ValueError(f"Unable to make prediction for {disease_type}")

            from explainability import get_feature_importance
            explanations = get_feature_importance(model, values, model_features, disease_type)

            return render_template(
                'predict.html',
                pred=prediction,
                confidence=confidence,
                disease_type=disease_type,
                form_data=form_data,
                explanations=explanations
            )

    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return render_template(
            'predict.html',
            pred=None,
            confidence=0,
            disease_type=disease_type,
            form_data=request.form.to_dict() if request.form else {}
        )


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


from db import init_db
from auth import init_auth
from routes_auth import auth_bp
from routes_user import user_bp
from routes_admin import admin_bp
from routes_logging_api import logging_bp
from routes_reports import reports_bp

init_db(app)
init_auth(app)

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(logging_bp)
app.register_blueprint(reports_bp)

try:
    with app.app_context():
        from db import db
        db.create_all()
except Exception:
    pass


if __name__ == "__main__":
    with app.app_context():
        try:
            from models import User, DiseasePrediction, ChatbotHistory, Report
            from db import db
            db.create_all()
        except Exception:
            pass
    app.run(host='0.0.0.0', port=3000, debug=True)
