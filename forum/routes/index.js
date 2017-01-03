var express = require('express');
var passport = require('passport');
var mongoose = require('mongoose');
var jwt = require('express-jwt');

var Post = mongoose.model('Post');
var Comment = mongoose.model('Comment');
var User = mongoose.model('User');
var Vote = mongoose.model('Vote');

var router = express.Router();
var auth = jwt({secret: 'SECRET', userProperty: 'payload'});


/* Router param ----------------------------------------------------------------------------------*/

// Preload posts
router.param('post', function(req, res, next, id) {
  var query = Post.findById(id);

  query.exec(function (err, post){
    if (err) { return next(err); }
    if (!post) { return next(new Error("Can't find post")); }

    req.post = post;
    return next();
  });
});

// Preload comments
router.param('comment', function(req, res, next, id) {
  var query = Comment.findById(id);

  query.exec(function (err, comment){
    if (err) { return next(err); }
    if (!comment) { return next(new Error("Can't find comment")); }

    req.comment = comment;
    return next();
  });
});

// Preload user
router.param('user', function(req, res, next, id) {
  var query = Post.findById(id);

  query.exec(function(err, user){
    if(err){ return next(err); }
    if(!user){ return next(new Error("Cannot find user.")); }

    req.user = user;
    return next();
  });
});

/* Routes ----------------------------------------------------------------------------------------*/

// Homepage
router.get('/', function(req, res) {
  res.render('index', { title: 'Express' });
});

// Get all posts
router.get('/posts', function(req, res, next) {
  Post.find(function(err, posts){
    if(err){ return next(err); }

    res.json(posts);
  });
});

router.get('/users', function(req, res, next) {
  User.find(function(err, users){
    if(err){ return next(err); }

    res.json(users);
  });
});

// Create new post
router.post('/posts', auth, function(req, res, next) {
  var post = new Post(req.body);
  post.author = req.payload.username;

  post.save(function(err, post){
    if(err){ return next(err); }

    res.json(post);
  });
});
/*router.post('/posts', auth, function(req, res, next){
  console.log(req.body);
  var jsonObj = {website: req.body.link};
  //json = {"website":req.body.link};
  $http.post('http://127.0.0.1:8080/scrape', jsonObj).success(function(error, response, body){
    if(error){ console.log("Error calling the scraping API."); }
    console.log(response);
    console.log(body);
  })
})
router.post('/posts', auth, function(req, res, next) {
  console.log()
  $http.post('http://127.0.0.1:8080/scrape', req.body).success(function(data){
    post.upvotes += 1;
  });
  fb.apiCall('GET', '/me/', {access_token: access_token}, function(error, response, body){ // access FB API
    // when FB responds this part of the code will execute
        if (error){
            throw new Error('Error getting user information');
        }
        body.platform = 'Facebook' // modify the Facebook response, available as JSON in body
        res.json(body); // send the response to client
    });
});*/

// Get single post
router.get('/posts/:post', function(req, res, next) {
  req.post.populate('comments', function(err, post) {
    res.json(post);
  });
});

router.put('/posts/:post/upvote', auth, function(req, res, next) {
  // Add user id to the list of upvoters
  req.post.upvoters.push(req.payload._id);
  // Remove user id from downvoters
  /*var index = req.post.downvoters.indexOf(req.payload._id);
  console.log(index);*/
  req.post.downvoters.remove(req.payload._id);
  req.post.upvotes += 1;
  req.post.save(function(err, post){
    if(err){ return next(err); }
    res.json(post);
  });
});

// downvote post
router.put('/posts/:post/downvote', auth, function(req, res, next) {
  req.post.downvoters.push(req.payload._id);
  /*var index = req.post.upvoters.indexOf(req.payload._id);
  console.log(index);
  req.post.upvoters.splice(index, 1);*/
  req.post.upvoters.remove(req.payload._id);
  req.post.upvotes -= 1;
  req.post.save(function(err, post){
    if(err){ return next(err); }
    res.json(post);
  });
});

// Get comments of a post
router.post('/posts/:post/comments', auth, function(req, res, next) {
  var comment = new Comment(req.body);
  comment.post = req.post;
  comment.author = req.payload.username;

  comment.save(function(err, comment){
    if(err){ return next(err); }

    req.post.comments.push(comment);
    req.post.save(function(err, post) {
      if(err){ return next(err); }

      res.json(comment);
    });
  });
});

// Upvote a comment
router.put('/posts/:post/comments/:comment/upvote', auth, function(req, res, next) {
  req.comment.upvote(function(err, comment){
    if(err){ return next(err); }

    res.json(comment);
  });
});

// Downvote a comment
router.put('/posts/:post/comments/:comment/downvote', auth, function(req, res, next) {
  req.comment.downvote(function(err, comment){
    if(err){ return next(err); }

    res.json(comment);
  });
});

// Register a new user
router.post('/register', function(req, res, next) {
  if(!req.body.username || !req.body.password) {
    return res.status(400).json({message: 'Some fields are missing.'});
  }

  var user = new User();
  user.username = req.body.username;
  user.setPassword(req.body.password);
  user.save(function(err) {
    if(err) { return next(err); }

    return res.json({token: user.generateJWT()});
  });
});

// Login user
router.post('/login', function(req, res, next) {
  if(!req.body.username || !req.body.password) {
    return res.status(400).json({message: 'Some fields are missing.'});
  }
  // use LocalStrategy for authentication
  passport.authenticate('local', function(err, user, info){
    if(err) { return next(err); }
    if(user) {
      return res.json({token: user.generateJWT()});
    }
    else {
      return res.status(401).json(info);
    }
  })(req, res, next);
});



module.exports = router;
