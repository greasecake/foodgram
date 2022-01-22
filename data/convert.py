import json


ingredients_prepared = []

with open('ingredients.json', 'r', encoding='utf-8') as input_file:
    data = json.load(input_file)
    for i, el in enumerate(data):
        ingredients_prepared += [{
            'model': 'recipes.ingredient',
            'pk': i,
            'fields': el
        }]

with open('../backend/foodgram/fixtures/ingredients_prepared.json', 'w', encoding='utf-8') as output_file:
    output_file.write(json.dumps(ingredients_prepared, ensure_ascii=False))
