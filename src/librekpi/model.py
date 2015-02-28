"""Model

This module descibes DB models/entities implementation
"""


import calendar
import os
from base64 import b64decode, b64encode
from datetime import datetime, timedelta
from hashlib import sha256

from sqlalchemy import Column, Integer, UnicodeText, Date, DateTime, String, \
    BigInteger, Enum, SmallInteger, Float, func, text, \
    Boolean, ForeignKey
from sqlalchemy.orm import deferred, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()
metadata = Base.metadata

from sqlalchemy.types import TypeDecorator, VARCHAR
import json

import logging


logger = logging.getLogger(__name__)

class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage:

        JSONEncodedDict(255)

    """

    impl = VARCHAR
    empty_val = {}

    def process_bind_param(self, value, dialect):
        logger.debug(value)
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        return json.loads(value) if value is not None else self.empty_val

class JSONEncodedList(JSONEncodedDict):
    """Represents an immutable structure as a json-encoded string.

    Usage:

        JSONEncodedDict(255)

    """

    empty_val = []

__all__ = ["User", "SocialAuth",
           "Teacher", "Course",
           "Comment", "Rating"]


class User(Base):
    """
    Typical User description
    """

    __tablename__ = "users"


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    id = Column(Integer, autoincrement=True, primary_key=True)
    fbid = Column(BigInteger, unique=True, index=True)  # ?
    username = Column(String(35), unique=True, index=True)
    role = Column(Enum('administrator', 'moderator', 'student',  # not need for `teacher` role
                       name="role"), default='student', nullable=False)

    displayname = Column(String(64), nullable=False)

    email = Column(String(64), unique=True, nullable=False, index=True)

    _salt = Column("salt", String(12))

    @hybrid_property
    def salt(self):
        """Generates a cryptographically random salt and sets its Base64 encoded
        version to the salt column, and returns the encoded salt.
        """
        if not self.id and not self._salt:
            self._salt = b64encode(os.urandom(8))

        if isinstance(self._salt, str):
            self._salt = self._salt.encode('UTF-8')

        return self._salt

    # 64 is the length of the SHA-256 encoded string length
    _password = Column("password", String(64))

    def __encrypt_password(self, password, salt):
        """
        Encrypts the password with the given salt using SHA-256. The salt must
        be cryptographically random bytes.

        :param password: the password that was provided by the user to try and
                         authenticate. This is the clear text version that we
                         will need to match against the encrypted one in the
                         database.
        :type password: basestring

        :param salt: the salt is used to strengthen the supplied password
                     against dictionary attacks.
        :type salt: an 8-byte long cryptographically random byte string
        """

        if isinstance(password, str):
            password_bytes = password.encode("UTF-8")
        else:
            password_bytes = password

        hashed_password = sha256()
        hashed_password.update(password_bytes)
        hashed_password.update(salt)
        hashed_password = hashed_password.hexdigest()

        if not isinstance(hashed_password, str):
            hashed_password = hashed_password.decode("UTF-8")

        return hashed_password

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = self.__encrypt_password(password,
                                                 b64decode(str(self.salt)))

    def validate_password(self, password):
        """Check the password against existing credentials.

        :type password: str
        :param password: clear text password
        :rtype: bool
        """
        return self.password == self.__encrypt_password(password,
                                                        b64decode(str(self.salt)))


    city = Column(String(30), default=None, index=True)

    gender = Column(Enum('male', 'female', name="gender"), nullable=True)
    date_of_birth = Column(Date)

    @hybrid_property
    def age(self):
        """Property calculated from (current time - :attr:`User.date_of_birth` - leap days)"""
        if self.date_of_birth:
            today = (datetime.utcnow() + timedelta(hours=self.timezone)).date()
            birthday = self.date_of_birth
            if isinstance(birthday, datetime):
                birthday = birthday.date()
            age = today - (birthday or (today - timedelta(1)))
            return (age.days - calendar.leapdays(birthday.year, today.year)) / 365
        return -1

    @age.expression
    def age(cls):
        return func.date_part("year", func.age(cls.date_of_birth))

    locale = Column(String(10))
    timezone = Column(SmallInteger)

    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=True,
                        index=True, unique=True)  # is_teacher: NOT NULL

    created = Column(DateTime, default=datetime.utcnow,
                     server_default=text("now()"), nullable=False)
    lastmodified = Column(DateTime, default=datetime.utcnow,
                          server_default=text("now()"), nullable=False)
    lastaccessed = Column(DateTime, default=datetime.utcnow,
                          server_default=text("now()"), nullable=False)


class SocialAuth(Base):
    """
    Typical Social User description
    """

    __tablename__ = "users_social"


    def __init__(self, **kwargs):
        super(SocialAuth, self).__init__(**kwargs)

    # TODO: add multi uniq

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    soc_id = Column(BigInteger, unique=True, index=True)
    token = Column(String(64))
    soc_data = Column(JSONEncodedDict(1024))


class Teacher(Base):
    """
    Typical Teacher description
    """

    __tablename__ = "teachers"


    def __init__(self, **kwargs):
        super(Teacher, self).__init__(**kwargs)

    id = Column(Integer, autoincrement=True, primary_key=True)

    name = Column(String(35), nullable=False)           # ім’я
    midinit = Column(String(35), nullable=False)        # по-батькові
    surname = Column(String(35), nullable=False)        # прізвище

    photo = deferred(Column(UnicodeText))
    courses = relationship("Course", backref="teacher")

    faculty = Column(String(64), nullable=False)        # where teacher works
    departments = deferred(Column(JSONEncodedList(512)))   # where he tells lectures

    bio = deferred(Column(UnicodeText))

    degree = Column(String(35), nullable=False)         # academic degree
    position = Column(String(35), nullable=False)

    publications = deferred(Column(JSONEncodedDict(512)))  # title-link-whatever structure

    contacts = deferred(Column(UnicodeText))            # TODO: decide m/b JSON?

    # TODO: decide -> courses_tags = just distinct all course tags?

    created = Column(DateTime, default=datetime.utcnow,
                     server_default=text("now()"), nullable=False)
    lastmodified = Column(DateTime, default=datetime.utcnow,
                          server_default=text("now()"), nullable=False)
    lastaccessed = Column(DateTime, default=datetime.utcnow,
                          server_default=text("now()"), nullable=False)


class Course(Base):
    """
    Typical Teacher description
    """

    __tablename__ = "courses"


    def __init__(self, **kwargs):
        super(Course, self).__init__(**kwargs)

    id = Column(Integer, autoincrement=True, primary_key=True)

    icon = deferred(Column(UnicodeText))

    title = Column(String(64), nullable=False)

    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False, index=True)

    tags = deferred(Column(JSONEncodedList(512)))

    description = deferred(Column(UnicodeText))

    schedule = deferred(Column(JSONEncodedDict(512)))  # TODO: clarify structure

    topics = deferred(Column(JSONEncodedList(512)))

    comments = relationship('Comment', backref='course')


class Rating(Base):
    """
    Typical Teacher description
    """

    __tablename__ = "ratings"


    def __init__(self, **kwargs):
        super(Rating, self).__init__(**kwargs)

    id = Column(Integer, autoincrement=True, primary_key=True)

    entity_type = Column(Enum('teacher', 'course'), nullable=False)
    entity_id = Column(Integer, nullable=False)
    value = Column(Enum('A', 'B', 'C', 'D', 'E', 'F', 'Fx'), nullable=False)
    voter = relationship('User', backref='votes')


class Comment(Base):
    """
    Disqus comment
    """

    __tablename__ = "comments"


    def __init__(self, **kwargs):
        super(Comment, self).__init__(**kwargs)

    id = Column(Integer, autoincrement=True, primary_key=True)

    user_id = relationship('User', backref='comments')

    reply_to = relationship('Comment', backref='replies')

    text = Column(UnicodeText)
    created = Column(DateTime, default=datetime.utcnow, nullable=False)
