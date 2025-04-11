from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import pandas as pd
from typing import List, Dict, Optional

app = Flask(__name__)

# Configure professional blue color scheme
app.config['SITE_THEME'] = {
    'primary': '#2c3e50',
    'secondary': '#3498db',
    'accent': '#e74c3c',
    'light': '#ecf0f1',
    'dark': '#2c3e50',
    'success': '#27ae60',
    'info': '#2980b9',
    'warning': '#f39c12',
    'danger': '#e74c3c'
}

# Load the models with error handling
try:
    with open('models/course_data.pkl', 'rb') as f:
        course_data = pickle.load(f)
    with open('models/similarity.pkl', 'rb') as f:
        similarity = pickle.load(f)
    with open('models/course_list.pkl', 'rb') as f:
        course_list = pickle.load(f)
except FileNotFoundError as e:
    print(f"Error: Model file not found - {e}")
    exit(1)
except Exception as e:
    print(f"Error loading model files: {e}")
    exit(1)

# Convert to numpy arrays for better performance
course_list = np.array(course_list)
similarity = np.array(similarity)
courses_df = pd.DataFrame(course_data)
course_url_dict = {course['course_name']: course['course_url'] for course in course_data}

def recommend_courses(course_name: str) -> List[Dict[str, str]]:
    """Recommend similar courses based on input course name."""
    try:
        matches = np.where(course_list == course_name)[0]
        if len(matches) == 0:
            return []
        idx = matches[0]
        sim_scores = sorted(list(enumerate(similarity[idx])), key=lambda x: x[1], reverse=True)
        return [{
            'name': course_list[i[0]],
            'url': course_url_dict.get(course_list[i[0]], '#')
        } for i in sim_scores[1:7]]  # Top 6 recommendations
    except Exception as e:
        print(f"Recommendation error: {e}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    recommendations = []
    selected_course = None
    
    if request.method == 'POST':
        selected_course = request.form.get('course_name', '').strip()
        if selected_course:
            recommendations = recommend_courses(selected_course)
            if not recommendations:
                error = f"No recommendations found for '{selected_course}'. Please try another course."
        else:
            error = "Please enter a course name"
    
    return render_template('index.html',
                        theme=app.config['SITE_THEME'],
                        courses=course_list.tolist(),
                        recommendations=recommendations,
                        selected_course=selected_course,
                        error=error)

@app.route('/about')
def about():
    return render_template('about.html', theme=app.config['SITE_THEME'])

@app.route('/autocomplete')
def autocomplete():
    search_term = request.args.get('term', '').lower()
    suggestions = [course for course in course_list if search_term in course.lower()]
    return jsonify(suggestions[:10])

if __name__ == '__main__':
    app.run(debug=True)