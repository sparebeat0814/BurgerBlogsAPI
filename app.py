# from email.mime import image

from lib2to3.pgen2 import token
from venv import create
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS 
import os

# from sqlalchemy import false


app = Flask( __name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)
app.config['CORS_HEADERS'] = "application/json"
app.config["JWT_SECRET_KEY"] = "Do-You-Want-Fries-With-That"  # Change this "super secret" with something else!
jwt = JWTManager(app)



class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False)
    content = db.Column(db.String(144), unique=False)
    imageURL = db.Column(db.String(144), unique=False)
    
    

    def __init__(self, title, content, imageURL):
        self.title = title
        self.content = content
        self.imageURL = imageURL


class BlogSchema(ma.Schema):
    class Meta:
        fields = ('title', 'content', 'imageURL','id')


blog_schema = BlogSchema()
blogs_schema = BlogSchema(many=True)

# Endpoint to create a new guide
@app.route('/blog', methods=["POST"])
def add_blog():
    # id = request.json['id']
    title = request.json['title']
    content = request.json['content']
    imageURL = request.json['imageURL']

    new_blog = Blog(title, content, imageURL)

    db.session.add(new_blog)
    db.session.commit()

    blog = Blog.query.get(new_blog.id)

    return blog_schema.jsonify(blog)


# Endpoint to query all guides
@app.route("/blogs", methods=["GET"])
def get_blogs():
    all_blogs = Blog.query.all()
    result = blogs_schema.dump(all_blogs)
    return jsonify(result)


# Endpoint for querying a single guide
@app.route("/blog/<id>", methods=["GET"])
def get_blog(id):
    blog = Blog.query.get(id)
    return blog_schema.jsonify(blog)


# Endpoint for updating a guide
@app.route("/blog/<id>", methods=["PUT"])
def guide_update(id):
    blog = Blog.query.get(id)
    title = request.json['title']
    content = request.json['content']
    imageURL = request.json['imageURL']

    blog.title = title
    blog.content = content
    blog.imageURL = imageURL

    db.session.commit()
    return blog_schema.jsonify(blog)


# Endpoint for deleting a record
@app.route("/blog/<id>", methods=["DELETE"])
def blog_delete(id):
    blog = Blog.query.get(id)
    db.session.delete(blog)
    db.session.commit()

    return "Blog was successfully deleted"


    # all authentication



class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    # primary_key= True

    def __init__(self, username, password):
        self.username = username
        self.password = password
        

class UserSchema(ma.Schema):     
    class Meta:
        fields = ('user_id','username', 'password')


user_schema = UserSchema()


#JWT endpoint
# Create a route to authenticate your users and return JWT Token. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/token", methods=["POST"])
def create_token():
    username = request.json.get("username")
    password = request.json.get("password")
   
    # Query your database for username and password
    user = User.query.filter_by(username=username, password=password).first()
    # print("--->",user.username)
    if user is None:
        # the user was not found on the database
        return jsonify({"msg": "Bad username or password"}), 401
    
    # create a new token with the user id inside
    access_token = create_access_token(identity=user.username)
    refresh_token = create_refresh_token(identity=user.username)
    #segments = access_token.split('.')
    return jsonify({ "token": access_token, "username": user.username }), 200
 
#endpoint to create a user


@app.route("/user", methods=["POST"])
def create_user():
    username = request.json['username']
    password = request.json['password']


    new_user = User(username, password)

    db.session.add(new_user)
    db.session.commit()

    user = User.query.get(new_user.user_id)

    return user_schema.jsonify(user)

# endpoint to delete a user
@app.route("/user/<user_id>", methods=["DELETE"])
def user_delete(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()

    return "user was deleted"





# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/protected", methods=["GET"])
@jwt_required()
#@jwt_required(fresh=True)
def protected():
    # Access the identity of the current user with get_jwt_identity
    username = get_jwt_identity()
    print(username)
    user=db.session.query(User).filter_by(username=username).first()
    #user = User.query.get(username)
    
    return jsonify({ "id":user.user_id,"username": user.username }), 200






if __name__ == '__main__':
    app.run(debug=True)
