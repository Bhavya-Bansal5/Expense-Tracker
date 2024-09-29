from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)

# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    expenses = Expense.query.all()
    budget = Budget.query.first()
    total_expense = sum(exp.amount for exp in expenses)
    remaining_budget = budget.amount - total_expense if budget else 0
    return render_template('index.html', expenses=expenses, total_expense=total_expense, remaining_budget=remaining_budget, budget=budget)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    description = request.form['description']
    amount = request.form['amount']
    if not description or not amount:
        flash('Both fields are required!', 'error')
        return redirect(url_for('index'))
    
    new_expense = Expense(description=description, amount=float(amount))
    db.session.add(new_expense)
    db.session.commit()
    flash('Expense added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/set_budget', methods=['POST'])
def set_budget():
    amount = request.form['budget']
    if not amount:
        flash('Budget amount is required!', 'error')
        return redirect(url_for('index'))
    
    budget = Budget.query.first()
    if budget:
        budget.amount = float(amount)
    else:
        budget = Budget(amount=float(amount))
        db.session.add(budget)

    db.session.commit()
    flash('Budget set successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_expense/<int:id>', methods=['POST'])
def delete_expense(id):
    expense = Expense.query.get(id)
    if expense:
        db.session.delete(expense)
        db.session.commit()
        flash('Expense deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
