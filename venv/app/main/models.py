from hashlib import md5
from main import db
import flask.ext.whooshalchemy as whooshalchemy
from main import app


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

pollers = db.Table(
	'pollers',
	db.Column('poll_id', db.Integer, db.ForeignKey('poll.id')),
	db.Column('poller_id', db.Integer, db.ForeignKey('user.id'))
)

class Poll(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, unique=True)
	positive = db.Column(db.Integer, default=0)

	polled = db.relationship('User',
							   secondary=pollers,
							   
							   backref=db.backref('pollers', lazy='dynamic'),
							   lazy='dynamic')



	def __init__(self, name, positive=None):
		self.name = name
		if positive is None:
			positive = 1
		self.positive = positive
	

	def get_id(self):
		try:
			return unicode(self.id)  # python 2
		except NameError:
			return str(self.id)  # python 3
			
	def poll(self, user):
		if not self.is_polling(user):
			self.polled.append(user)
			
			return self

	def unpoll(self, user):
		if self.is_polling(user):
			self.polled.remove(user)
			return self

	def is_polling(self, user):
		return self.polled.filter(
			pollers.c.poller_id == user.id).count() > 0

	def poll_count(self):
		return self.polled.filter(
			pollers.c.poller_id).count()
        
        def vote_up(self, user):
            if self.is_polling(user):
                
                
                return self.positive
            
        def vote_down(self, user):
           if self.is_polling(user):
               negative = 0
               negative = negative +1
               return negative

	def __repr__(self):
		return '<Poll %r>' % (self.name)

				
class User(db.Model):


	id = db.Column(db.Integer, primary_key=True)
	nickname = db.Column(db.String(64), index=True, unique=True)

	email = db.Column(db.String(120), index=True, unique=True)
	password = db.Column(db.String(255))
	age = db.Column(db.Integer, default=0)
	address = db.Column(db.Integer, default=0)
	county = db.Column(db.String(64))
	constituency = db.Column(db.String(64))
	ward = db.Column(db.String(64))
		
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	   
	last_seen = db.Column(db.DateTime)
	followed = db.relationship('User',
							   secondary=followers,
							   primaryjoin=(followers.c.follower_id == id),
							   secondaryjoin=(followers.c.followed_id == id),
							   backref=db.backref('followers', lazy='dynamic'),
							   lazy='dynamic')

	@staticmethod
	def make_unique_nickname(nickname):
		if User.query.filter_by(nickname=nickname).first() is None:
			return nickname
		version = 2
		while True:
			new_nickname = nickname + str(version)
			if User.query.filter_by(nickname=new_nickname).first() is None:
				break
			version += 1
		return new_nickname

	def __init__(self, nickname, password, email, age, address, county, constituency, ward):
		self.nickname = nickname
		self.password = password
		self.email = email            
		self.age = age
		self.address = address
		self.county = county
		self.constituency = constituency
		self.ward = ward
    
    
	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		try:
		    return unicode(self.id)  # python 2
		except NameError:
		    return str(self.id)  # python 3

	def avatar(self, size):
		return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % \
			(md5(self.email.encode('utf-8')).hexdigest(), size)

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)
			return self

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)
			return self

	def is_following(self, user):
		return self.followed.filter(
			followers.c.followed_id == user.id).count() > 0

	def followed_posts(self):
		return Post.query.join(
			followers, (followers.c.followed_id == Post.user_id)).filter(
				followers.c.follower_id == self.id).order_by(
					Post.timestamp.desc())

	def followed_polls(self):
		return Poll.query.join(pollers, (pollers.c.poller_id == Poll.id)).filter(pollers.c.poll_id == self.id)

	def __repr__(self):
		return '<User %r>' % (self.nickname)


class Post(db.Model):
	__searchable__ =['body']

	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post %r>' % (self.body)

whooshalchemy.whoosh_index(app, Post)
