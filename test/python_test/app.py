from flask import Flask, render_template, request, jsonify
from stance_detector import StanceDetector, StanceDetectionError
import os
from dotenv import load_dotenv
import asyncio


app = Flask(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
detector = StanceDetector(api_key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        text = data.get('text', '').strip()
        detection_type = data.get('type', '').upper()
        target = data.get('target', '').strip() if detection_type == 'E' else None

        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400
        if detection_type == 'E' and not target:
            return jsonify({'error': 'Target is required for explicit stance detection'}), 400

        # Run async detection in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analysis = loop.run_until_complete(detector.detect_stance(text, target))
        loop.close()

        return jsonify({
            'text': analysis.text,
            'target': analysis.target,
            'stance': analysis.stance,
            'confidence': analysis.confidence,
            'explanation': analysis.explanation
        })

    except StanceDetectionError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True) 