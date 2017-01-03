var mongoose = require('mongoose');

var VoteSchema = new mongoose.Schema({
  user: {type: mongoose.Schema.Types.ObjectId, ref:'User'},
  item: {type: mongoose.Schema.Types.ObjectId, ref:'Post'},
  value: {type: Number, default: 0}
});

mongoose.model('Vote', VoteSchema);
