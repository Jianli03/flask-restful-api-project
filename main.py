
from flask import Flask
from flask_restful import Api, Resource, abort, marshal_with, reqparse, fields
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

 # create a model
class VideoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    views = db.Column(db.Integer, nullable=False)
    likes = db.Column(db.Integer, nullable=False)


    def __repr__(self):
        return f"VideoModel(name={self.name}, views={self.views}, likes={self.likes})"

# Ensure the database is created only when necessary
@app.before_first_request
def create_tables():
    db.create_all()

video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help="name of the video", required=True)
video_put_args.add_argument("views", type=int, help="Number of views", required=True)
video_put_args.add_argument("likes", type=int, help="Number of likes", required=True)


video_update_args = reqparse.RequestParser()
video_update_args.add_argument("name", type=str, help="name of the video")
video_update_args.add_argument("views", type=int, help="Number of views")
video_update_args.add_argument("likes", type=int, help="Number of likes")


resource_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "views": fields.Integer,
    "likes": fields.Integer
}

class Video(Resource):
    @marshal_with(resource_fields)
    def get(self, video_id):
        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort(404, message="Video not found...")
        return result

    @marshal_with(resource_fields)
    def put(self, video_id):

        args = video_put_args.parse_args()

        result = VideoModel.query.filter_by(id=video_id).first()
        if result:
            abort(409, message="Video already exists with that ID...")
        video = VideoModel(id=video_id, name=args["name"], views=args["views"], likes=args["likes"])
        db.session.add(video)
        db.session.commit()

        return video, 201

    @marshal_with(resource_fields)
    def patch(self, video_id):
        args = video_update_args.parse_args()
        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort(404, message="Video not found...can not update")

        if args["name"]:
            result.name = args["name"]
        if args["views"]:
            result.views = args["views"]
        if args["likes"]:
            result.likes = args["likes"]

        db.session.commit()
        return result

    @marshal_with(resource_fields)
    def delete(self, video_id):
        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort(404, message="Video not found...")

        db.session.delete(result)
        db.session.commit()
        return "", 204


api.add_resource(Video, "/video/<int:video_id>")

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
