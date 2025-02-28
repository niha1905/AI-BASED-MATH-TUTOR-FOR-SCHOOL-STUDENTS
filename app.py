from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import sympy
import manim
import numpy as np
import io
import base64
import os
import tempfile
import shutil
import google.generativeai as genai
import os
import re
import sympy as sp
import numpy as np
import base64
import tempfile
import shutil
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import manim
import google.generativeai as genai
import os
import re
import sympy as sp
import numpy as np
import base64
import tempfile
import shutil

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import manim
import google.generativeai as genai


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

genai.configure(api_key="Gemini api key")
socketio = SocketIO(app, cors_allowed_origins="*")
x, y = sp.symbols('x y')

def fix_multiplication(equation_str):
    
    equation_str = equation_str.replace("^", "**")  # Convert '^' to '**'
    equation_str = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", equation_str)  # 2x -> 2*x
    equation_str = re.sub(r"([a-zA-Z])([a-zA-Z])", r"\1*\2", equation_str)  # xy -> x*y
    equation_str = re.sub(r"(sin|cos|tan|exp|log|sqrt)\*", r"\1", equation_str)  # Fix trig functions
    return equation_str

import re

import re

def format_explanation(explanation):
    """Convert AI explanation to HTML by preserving line breaks and formatting."""
    formatted = explanation.replace("\n", "<br>")  # Preserve new lines
    formatted = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", formatted)  # Convert **bold** to <strong>
    formatted = re.sub(r"\*(.*?)\*", r"<em>\1</em>", formatted)  # Convert *italic* to <em>
    formatted = re.sub(r"```(.*?)```", r"<pre>\1</pre>", formatted, flags=re.DOTALL)  # Format code blocks
    return formatted

def get_ai_explanation(equation_str):
    """Generate a step-by-step AI explanation using Google Gemini API."""
    prompt = f"Explain step by step how to solve this equation in a professional format: {equation_str}"
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        explanation = response.text if response.text else "AI explanation unavailable."
        return format_explanation(explanation)  # Apply formatting before returning
    except Exception as e:
        return f"AI explanation error: {str(e)}"


    
 

@socketio.on('process_equation')
def process_equation(data):

    equation_str = data.get('equation', '').strip()

    try:
        equation_str = fix_multiplication(equation_str)
        equation = sp.sympify(equation_str, evaluate=False) 
        ai_explanation = get_ai_explanation(equation_str)
        ai_explanation = format_explanation(ai_explanation)  
        emit('equation_processed', {
            'animation': manim_animation,
            'explanation': ai_explanation
        })

    except (sp.SympifyError, ValueError, TypeError) as e:
        emit('equation_error', {'error': f"Invalid equation: {str(e)}"})
    except Exception as e:
        emit('equation_error', {'error': f"Unexpected error: {str(e)}"})


        class EquationScene(manim.Scene):
            def construct(self):
                ax = manim.Axes(
                    x_range=[-10, 10, 1], y_range=[-10, 10, 1],
                    axis_config={"color": manim.WHITE}
                )
                self.add(ax)

                try:
                    sympy_func = sp.lambdify(x, equation, "numpy")
                    numpy_func = np.vectorize(sympy_func)
                    graph = ax.plot(numpy_func, color=manim.BLUE)
                    self.play(manim.Create(graph))
                except Exception:
                    text = manim.Text("Complex/non-polynomial equation detected. Showing implicit plot.", color=manim.YELLOW)
                    self.play(manim.Write(text))
                    implicit_plot = ax.plot_implicit_curve(lambda x, y: sp.re(equation.subs({'x': x, 'y': y})), color=manim.RED)
                    self.play(manim.Create(implicit_plot))
                
                self.wait(2)

        with tempfile.TemporaryDirectory() as temp_dir:
            scene = EquationScene()
            scene.render()
            media_dir = os.path.join(os.getcwd(), "media", "videos", "1080p60")
            if not os.path.exists(media_dir):
                emit('equation_error', {'error': "Manim output directory not found."})
                return

            video_files = [f for f in os.listdir(media_dir) if f.endswith(".mp4")]
            if not video_files:
                emit('equation_error', {'error': "No video output found. Manim rendering may have failed."})
                return

            latest_video = max(video_files, key=lambda f: os.path.getmtime(os.path.join(media_dir, f)))
            rendered_file = os.path.join(media_dir, latest_video)

            with open(rendered_file, "rb") as f:
                video_bytes = f.read()

            video_base64 = base64.b64encode(video_bytes).decode()
            manim_animation = f"data:video/mp4;base64,{video_base64}"

        emit('equation_processed', {'animation': manim_animation, 'explanation': ai_explanation})

    except (sp.SympifyError, ValueError, TypeError) as e:
        emit('equation_error', {'error': f"Invalid equation: {str(e)}"})
    except Exception as e:
        emit('equation_error', {'error': f"Unexpected error: {str(e)}"})

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/solve')
def solve():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)

