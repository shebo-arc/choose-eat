from flask import Flask, request

app = Flask(__name__)

# Route to serve the HTML page
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bullet Point Selector</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 20px;
            }
            label {
                display: block;
                margin-bottom: 10px;
            }
            input[type="text"] {
                width: 100%;
                padding: 8px;
                margin-bottom: 20px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            ul {
                list-style-type: none;
                padding-left: 0;
            }
            li {
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>

        <h1>Bullet Point Selector</h1>

        <form id="bulletForm" method="POST" action="/submit">
            <!-- Selectable bullet points -->
            <label>Select bullet points:</label>
            <ul>
                <li><input type="checkbox" name="bullets" value="Bullet Point 1"> Bullet Point 1</li>
                <li><input type="checkbox" name="bullets" value="Bullet Point 2"> Bullet Point 2</li>
                <li><input type="checkbox" name="bullets" value="Bullet Point 3"> Bullet Point 3</li>
            </ul>

            <!-- Submit button -->
            <button type="submit">Submit</button>
        </form>

    </body>
    </html>
    '''

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    # Get selected bullet points
    selected_bullets = request.form.getlist('bullets')

    # Print the results in the Python shell
    print(f"Selected bullet points: {', '.join(selected_bullets)}")

    # Return a response to the user
    return f'''
    <h2>Form submitted successfully!</h2>
    <p>Selected bullet points: {', '.join(selected_bullets)}</p>
    <a href="/">Go back</a>
    '''

if __name__ == '__main__':
    app.run(debug=True)
