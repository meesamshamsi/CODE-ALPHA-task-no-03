from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, unique=True, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'), nullable=False)
    status = db.Column(db.String(50), default="Pending")

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

# API Endpoints
@app.route('/menu', methods=['GET', 'POST'])
def manage_menu():
    if request.method == 'POST':
        data = request.get_json()
        item = MenuItem(name=data['name'], price=data['price'])
        db.session.add(item)
        db.session.commit()
        return jsonify({"message": "Menu item added", "id": item.id}), 201
    items = MenuItem.query.all()
    return jsonify([{"id": i.id, "name": i.name, "price": i.price} for i in items])

@app.route('/tables', methods=['GET', 'POST'])
def manage_tables():
    if request.method == 'POST':
        data = request.get_json()
        table = Table(table_number=data['table_number'])
        db.session.add(table)
        db.session.commit()
        return jsonify({"message": "Table added", "id": table.id}), 201
    tables = Table.query.all()
    return jsonify([{"id": t.id, "table_number": t.table_number, "is_available": t.is_available} for t in tables])

@app.route('/reservations', methods=['POST'])
def reserve_table():
    data = request.get_json()
    table = Table.query.get_or_404(data['table_id'])
    if not table.is_available:
        return jsonify({"error": "Table is not available"}), 400
    
    table.is_available = False
    reservation = Reservation(customer_name=data['customer_name'], table_id=table.id)
    db.session.add(reservation)
    db.session.commit()
    return jsonify({"message": "Table reserved successfully"}), 201

@app.route('/orders', methods=['POST'])
def place_order():
    if request.is_json:
        data = request.get_json()
        table_id = data.get('table_id')
    else:
        table_id = request.args.get('table_id')
        
    order = Order(table_id=table_id)
    db.session.add(order)
    db.session.commit()
    return jsonify({"message": "Order placed successfully", "order_id": order.id}), 201

@app.route('/inventory', methods=['GET', 'POST', 'PUT'])
def manage_inventory():
    if request.method == 'POST':
        data = request.get_json()
        inv = InventoryItem(item_name=data['item_name'], quantity=data['quantity'])
        db.session.add(inv)
        db.session.commit()
        return jsonify({"message": "Inventory item added", "id": inv.id}), 201
    elif request.method == 'PUT':
        data = request.get_json()
        inv = InventoryItem.query.get_or_404(data['id'])
        inv.quantity = data['quantity']
        db.session.commit()
        return jsonify({"message": "Inventory updated"})
    items = InventoryItem.query.all()
    return jsonify([{"id": i.id, "item_name": i.item_name, "quantity": i.quantity} for i in items])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
