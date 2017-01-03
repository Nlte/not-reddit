var mongoose = require('mongoose');
var crypto = require('crypto');
var jwt = require('jsonwebtoken');

// TODO : Cipher password (hash+salt) ==> don't store it in clear !

var UserSchema = new mongoose.Schema({
  username: {type: String, lowercase: true, unique: true},
  password: String,
});

UserSchema.methods.setPassword = function(password) {
  this.password = password;
};

UserSchema.methods.validPassword = function(password) {
  return this.password = password;
};

UserSchema.methods.generateJWT = function() {
  var today = new Date();
  var exp = new Date(today);
  exp.setDate(today.getDate() + 30);

  return jwt.sign({
    _id: this._id,
    username: this.username,
    exp: parseInt(exp.getTime() / 1000),
  }, 'SECRET');
};

mongoose.model('User', UserSchema);
