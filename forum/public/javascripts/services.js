angular.module('forum.services', []); //instantiates
angular.module('forum.services') //gets

.factory('posts', ['$http', 'auth', function($http, auth) {
  var o = {
    posts: []
  };

  o.getAll = function(){
    return $http.get('/posts').success(function(data){
      angular.copy(data, o.posts);
    });
  };

  o.create = function(post){
    console.log(post);
    var pattern = /^((http|https):\/\/)/;
    if(!pattern.test(post.link)) {
      console.log("Adding http protocol");
      post.link = "http://" + post.link;
    }
    $http.post('http://127.0.0.1:8080/scrape', post).success(function(data){
      new_post = {
        title: post.title,
        link: post.link,
        scraped: data,
      }
      console.log(new_post);
      return $http.post('/posts', new_post, {
        headers: {Authorization: 'Bearer ' + auth.getToken()}
      }).success(function(data){
        o.posts.push(data);
      });
    });
  };

  o.upvote = function(post){
    return $http.put('/posts/'+ post._id +'/upvote/', null, {
      headers: {Authorization: 'Bearer '+ auth.getToken()}
    }).success(function(data){
      post.upvotes += 1;
    });
  };

  o.downvote = function(post){
    return $http.put('/posts/'+ post._id +'/downvote/', null, {
      headers: {Authorization: 'Bearer '+ auth.getToken()}
    }).success(function(data){
      post.upvotes -= 1;
    });
  };

  o.get = function(id){
    return $http.get('/posts/'+ id).then(function(res){
      return res.data;
    });
  };

  o.addComment = function(id, comment){
    return $http.post('/posts/'+ id +'/comments', comment, {
      headers: {Authorization: 'Bearer '+ auth.getToken()}
    });
  };

  o.upvoteComment = function(post, comment){
    return $http.put('/posts/'+ post._id +'/comments/'+ comment._id +'/upvote', null, {
      headers: {Authorization: 'Bearer '+ auth.getToken()}
    }).success(function(data){
        comment.upvotes += 1;
      });
  };

  o.downvoteComment = function(post, comment){
    return $http.put('/posts/'+ post._id +'/comments/'+ comment._id +'/upvote', null, {
      headers: {Authorization: 'Bearer '+ auth.getToken()}
    }).success(function(data){
      comment.upvotes -= 1;
    });
  };

  return o;
}])

.factory('auth', ['$http', '$window', function($http, $window){
  var auth = {};

  auth.saveToken = function(token) {
    $window.localStorage['forum-news-token'] = token;
  }

  auth.getToken = function() {
    return $window.localStorage['forum-news-token'];
  }

  auth.isLoggedIn = function() {
    var token = auth.getToken();
    if(token) {
      var payload = JSON.parse($window.atob(token.split('.')[1]));
      return payload.exp > Date.now()/1000;
    } else {

      return false;
    }
  }

  auth.currentUser = function() {
    if(auth.isLoggedIn()) {
      var token = auth.getToken();
      var payload = JSON.parse($window.atob(token.split('.')[1]));

      return payload.username;
    }
  }

  auth.currentId = function() {
    if(auth.isLoggedIn()) {
      var token = auth.getToken();
      var payload = JSON.parse($window.atob(token.split('.')[1]));

      return payload._id;
    }
  }

  auth.register = function(user) {
    return $http.post('/register', user).success(function(data) {
      auth.saveToken(data.token);
    });
  }

  auth.login = function(user) {
    return $http.post('/login', user).success(function(data) {
      auth.saveToken(data.token);
    });
  }

  auth.logout = function() {
    $window.localStorage.removeItem('forum-news-token');
  }

  return auth;
}]);
