from flask import Flask, render_template, request, jsonify
import pandas as pd
from mcts_train import MCTS, read_food_data_from_csv, data_prune
import os

app = Flask(__name__, template_folder=os.path.abspath(os.path.dirname(__file__)))


@app.route('/')
def index():
    # Read available food categories
    df = pd.read_csv('filtered_food_data.csv')
    food_categories = df['food_category'].unique().tolist()
    return render_template('frontPage.html', food_categories=food_categories)


@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        # Get form data
        selected_categories = request.form.getlist('categories[]')
        calorie_weight = float(request.form['calorie_weight'])
        energy_weight = float(request.form['energy_weight'])
        calorie_limit = float(request.form['calorie_limit'])

        # Process the data using MCTS
        data_prune('filtered_food_data.csv', selected_categories)
        available_food_items = read_food_data_from_csv('pruned.csv')

        # Run MCTS optimization
        mcts = MCTS(available_food_items, calorie_limit, simulations=1000)
        best_food_plan = mcts.run(calorie_weight, energy_weight)

        # Prepare results
        results = []
        total_calories = 0
        total_energy = 0
        for food in best_food_plan:
            results.append({
                'name': food.name,
                'calories': food.calories,
                'energy': food.energy
            })
            total_calories += food.calories
            total_energy += food.energy

        return jsonify({
            'success': True,
            'food_plan': results,
            'total_calories': total_calories,
            'total_energy': total_energy
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


if __name__ == '__main__':
    app.run(debug=True)
