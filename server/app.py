from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza
import os

# Setup database path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# App and DB config
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Init DB and migration
db.init_app(app)
migrate = Migrate(app, db)

# Init API
api = Api(app)

@app.route("/")
def index():
    return "<h1>Pizza Restaurant API </h1>"


# Resource Classes


class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        # exclude restaurant_pizzas (handled by serialize_rules)
        return [r.to_dict() for r in restaurants], 200

class RestaurantByID(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        # Include restaurant_pizzas with nested pizza details
        return restaurant.to_dict(rules=("restaurant_pizzas", "restaurant_pizzas.pizza")), 200

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(restaurant)
        db.session.commit()
        return {}, 204

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [p.to_dict() for p in pizzas], 200

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            price = data.get("price")
            pizza_id = data.get("pizza_id")
            restaurant_id = data.get("restaurant_id")

            new_rp = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )

            db.session.add(new_rp)
            db.session.commit()

            # Return full nested object with pizza and restaurant details
            return new_rp.to_dict(rules=("pizza", "restaurant")), 201

        except Exception:
          return {"errors": ["validation errors"]}, 400


# Register Resources


api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantByID, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")


# Run App


if __name__ == "__main__":
    app.run(port=5555, debug=True)
