from email.mime import image
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

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
    title = request.json['title']
    content = request.json['content']
    imageURL = request.json['imageURL']

    new_blog = Blog(title, content, imageURL)

    db.session.add(new_blog)
    db.session.commit()

    blog = Blog.query.get(new_blog.id)

    return blog_schema.jsonify(blog)


# Endpoint to query all guides
@app.route("/blogss", methods=["GET"])
def get_blogs():
    all_blogs = Blog.query.all()
    result = blog_schema.dump(all_blogs)
    return jsonify(result.data)


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


#image endpoint
# @app.route('/get_image')
# def get_image():
#     if request.args.get('type') == '1':
#        filename = 'ok.gif'
#     else:
#        filename = 'error.gif'
#     return send_file(filename, mimetype='image/gif')


if __name__ == '__main__':
    app.run(debug=True)
