import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Get port from environment variable or choose 9099 as local default
port = int(os.getenv("PORT", 9099))


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://paxopprc:4Pk_SIhj0z1AxUgO0N12Y0BSnkaRsx-0@john.db.elephantsql.com:5432/paxopprc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Person(db.Model):
  __tablename__ = 'persons'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)

  def __repr__(self):
    return f'<Person ID: {self.id}, name: {self.name}>'

db.create_all()

@app.route('/')
def index():
  person = Person.query.first()
  return 'Hello ' + person.name

if __name__ == '__main__':
    # Run the app, listening on all IPs with our chosen port number
    app.run(host='0.0.0.0', port=port)
