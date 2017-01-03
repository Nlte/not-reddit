angular.module('forum.controllers', []); //instantiates
angular.module('forum.controllers') //gets

.controller('MainCtrl', [
  '$scope',
  'posts',
  'auth',
  function($scope, posts, auth){
    $scope.posts = posts.posts;
    $scope.isLoggedIn = auth.isLoggedIn;

    $scope.addPost = function() {
      if (!$scope.title || $scope.title === '') { return; }
      posts.create({
        title: $scope.title,
        link: $scope.link,
        upvotes: 0,
        comments: []
      });
      $scope.title = '';
      $scope.link = '';
    }

    /*$scope.hasUpvoted = function(post) {
      console.log(post);
      //console.log(post.upvoters.indexOf(auth.currentId()));
      if(post.upvoters.indexOf(auth.currentId()) != -1){
        return true;
      }else {
        return false;
      }
    }

    $scope.hasDownvoted = function(post) {
      console.log(post);
      //console.log(post.upvoters.indexOf(auth.currentId()));
      if(post.downvoters.indexOf(auth.currentId()) != -1){
        return true;
      }else {
        return false;
      }
    }*/

    $scope.incrementUpvotes = function(post) {
      if(!post.upvoted) {
        posts.upvote(post);
        post.upvoted = true;
        post.downvoted = false;
      }
    }

    $scope.decrementUpvotes = function(post) {
      if(!post.downvoted) {
        posts.downvote(post);
        post.downvoted = false;
        post.upvoted = true;
      }
    }

}])

.controller('PostsCtrl', [
  '$scope',
  '$stateParams',
  'posts',
  'post',
  'auth',
  function($scope, $stateParams, posts, post, auth) {
    $scope.post = post;
    $scope.isLoggedIn = auth.isLoggedIn;

    $scope.addComment = function() {
      if (!$scope.body || $scope.body === '') { return; }
      posts.addComment(post._id, {
        body: $scope.body,
        author: 'user',
        upvotes: 0,
      }).success(function(comment){
        $scope.post.comments.push(comment);
      });
      $scope.body = '';
    }

    $scope.incrementUpvotes = function(comment){
      posts.upvoteComment(post, comment);
    };

    $scope.decrementUpvotes = function(comment){
      posts.downvoteComment(post, comment);
    };

}])


.controller('AuthCtrl', ['$scope', '$state', 'auth', function($scope, $state, auth){
  $scope.user = {};

  $scope.register = function() {
    auth.register($scope.user).error(function(error){
      $scope.error = error;
    }).then(function() {
      $state.go('home');
    });
  }

  $scope.login = function() {
    auth.login($scope.user).error(function(error) {
      $scope.error = error;
    }).then(function() {
      $state.go('home');
    });
  }
}])


.controller('NavbarCtrl', ['$scope', 'auth', function($scope, auth) {
  $scope.isLoggedIn = auth.isLoggedIn;
  $scope.currentUser = auth.currentUser;
  $scope.logout = auth.logout;
}])


.controller('ProfileCtrl', ['$scope', 'auth', function($scope, auth) {
  $scope.currentUser = auth.currentUser;
}]);
