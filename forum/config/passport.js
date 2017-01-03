var passport = require('passport');
var LocalStrategy = require('passport-local').Strategy;
var mongoose = require('mongoose');
var User = mongoose.model('User');

// Custom strategy, only verifies username and password (with passwd method in Users model)
passport.use(new LocalStrategy(
  function(username, password, done) {
    User.findOne({ username: username }, function(err,user) {
      if(err) { return done(err); }
      if(!user) {
        return done(null, false, {message: 'Wrong username.'});
      }
      if(!user.validPassword(password)) {
        return done(null, false, {message: 'Wrong password.'});
      }
      return done(null, user);
    });
  }
));
