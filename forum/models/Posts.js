var mongoose = require('mongoose');

var PostSchema = new mongoose.Schema({
  title: String,
  link: String,
  author: String,
  scraped: String,
  upvotes: {type: Number, default: 0},
  upvoters: [String],
  downvoters: [String],
  comments: [{type: mongoose.Schema.Types.ObjectId, ref: 'Comment'}]
});

PostSchema.methods.upvote = function(callback){
  this.upvotes += 1;
  this.save(callback);
}

PostSchema.methods.downvote = function(callback){
  this.upvotes -= 1;
  this.save(callback);
}

PostSchema.methods.hasDownvoted = function(id, callback) {
  if(this.downvoters.indexOf(id) != -1){
    return true;
  }else{
    return false;
  }
}

PostSchema.methods.hasUpvoted = function(id, callback) {
  if(this.upvoters.indexOf(id) != -1){
    return true;
  }else{
    return false;
  }
}


mongoose.model('Post', PostSchema);
