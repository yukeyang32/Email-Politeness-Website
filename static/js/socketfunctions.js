var domain = document.domain;
var port = location.port;
var socket = io.connect('http://' + domain + ':' + port);

var politeness_data, sentiment_data, talktiveness;
var impolite_message, highlighted;
var posColor = '#EFEDE3', neuColor = '#EFEDE3', negColor = '#EFEDE3';
// politeness score and compound score across message and number of words for each user

// TODO: REFRESHING IS NOT WORKING PROPERLY (needs better way to deal with disconnect and reconnect)
// TODO: FLAG thing

$(document).ready(function(){

  $('#chat-wrapper').animate({scrollTop: $('#chat-wrapper').prop("scrollHeight")}, 100);

  $('#impoliteModal').on('show.bs.modal', function(){
    $('#impoliteModalBody').append(highlighted);
  });

  $('#impoliteModal').on('hide.bs.modal', function(){
    $('#impoliteModalBody p').remove();
  });

  $('#make-edits').click(function(){ // clicking make edits button
    $('#impoliteModal').modal('hide');
    $('#editModal').modal('show'); //show edit modal
    // send and cancel button
    $('#edit-send').click(submit_edits); //!this might not work

    $('#edit-cancel').click(function(){
      socket.emit( 'edit cancel', { // edit cancel
        user_name : username,
        message : impolite_message.message,
        time_stamp: getTime()
      });
      $('#editModal').modal('hide');
    });
  });

  $('#send-anyways').click(function(){ // clicking send anyways button
    socket.emit( 'send anyways', {
      user_name : username,
      message : impolite_message.message,
      time_stamp: getTime()
    });
    $('#impoliteModal').modal('hide');
  });

  $('#send-cancel').click(function(){
    socket.emit( 'send cancel', {
      user_name : username,
      message : impolite_message.message,
      time_stamp: getTime()
    });
  });

  $('#editModal').on('show.bs.modal', function(){
    console.log("edit modal opening");
    $('#org-msg').append(highlighted);
    $("#edit-input").append("<textarea class='mt-3' placeholder='Type the new message...' style='font-size: 18px; width:90%; border-radius:7px;'></textarea>");
    $("#edit-input textarea").focus();
    $("#edit-input textarea").keypress(function (e){
      if(e.which == 13 && !e.shiftKey){
        e.preventDefault()
        submit_edits();
      }
    });
  });

  $('#editModal').on('hide.bs.modal', function(){
    console.log("editmodal closed");
    $('#org-msg p').remove();
    $("#edit-input textarea").remove();
  });
});
//return the message with highlighted tokens
//TODO: fix the space issue (low priority)
function highlight(msg){
  var result = document.createElement('p');
  result.style.fontSize = "20px";
  result.style.marginBottom = "0";

  var i;
  for (i = 0; i < msg.tokens.length; i++) {
    var token = document.createElement("span");
    var text = document.createTextNode(msg.tokens[i] + '\xa0');
    if (msg.impolite_index.includes(i)){
      token.style.color = "red";
    }
    token.appendChild(text);
    result.appendChild(token);
  }
  return result;
}

function submit_edits(){
  var new_input = $("#edit-input textarea").val();
  socket.emit( 'send edited message',{
    user_name : username,
    message : new_input,
    time_stamp: getTime()});
  $('#editModal').modal('hide');
}

socket.on( 'connect', function() {
  /*
  user on connect:
  request previous messages
  ask server to broadcast its connection
  */
  socket.emit('new user connected', {
    name: username,
    entered : true
  })
  console.log("sent new user connected")

  // TODO: better way to deal with disconnect!! Refreshing does not work properly now!!
  window.addEventListener("beforeunload", function(){
    socket.emit('user disconnected', {
      name : username,
      entered: false
    })
  })

  var form = $( 'form' ).on( 'submit', function( e ) {
    e.preventDefault()
    send_message()
  })
  var form = $( "button" ).click( function( e ) {
    e.preventDefault()
    send_message()
  })
  $("#message").keypress(function (e){
    if(e.which == 13 && !e.shiftKey){
      e.preventDefault()
      send_message()
    }
  })
})

function send_message(){
  let user_input = $( 'textarea' ).val()
  socket.emit( 'send message', {
    user_name : username,
    message : user_input,
    time_stamp: getTime()
  } )
  $( 'textarea' ).val( '' ).focus()
}

socket.on('user change', function( msg ){
  let entered = msg.entered ? "entered" : "left"
  $('#chat-history').append('<div class="row float-right">'+msg.name+' has ' + entered + ' the chat room</div><br>');
  if(msg.entered){
    if (msg.name == username){
      $('#online-users').append('<li class="media"><div class="media-body"><span class="far fa-user-circle" style = "color: #EFEDE3 "></span> '+msg.name+'</div></li>');
    }
    else{
      $('#online-users').append('<li class="media"><div class="media-body"><span class="far fa-user-circle" style = "color: #EFEDE3"></span> '+msg.name+'</div></li>');
    }
  }
  else{
    $('#online-users li:contains("' + msg.name + '")').remove();
  }
  $('#chat-wrapper').animate({scrollTop: $('#chat-wrapper').prop("scrollHeight")}, 300);
})

// javascript for handling messages
var polite_score;

// TODO: Gradient color for sentiment maybe?
// This is a gradient from green to red based on input percentage
// var percentColors = [
//     { pct: 0.0, color: { r: 0xff, g: 0x00, b: 0 } },
//     { pct: 0.5, color: { r: 0xff, g: 0xff, b: 0 } },
//     { pct: 1.0, color: { r: 0x00, g: 0xff, b: 0 } } ];
//
// var getColorForPercentage = function(pct) {
//     for (var i = 1; i < percentColors.length - 1; i++) {
//         if (pct < percentColors[i].pct) {
//             break;
//         }
//     }
//     var lower = percentColors[i - 1];
//     var upper = percentColors[i];
//     var range = upper.pct - lower.pct;
//     var rangePct = (pct - lower.pct) / range;
//     var pctLower = 1 - rangePct;
//     var pctUpper = rangePct;
//     var color = {
//         r: Math.floor(lower.color.r * pctLower + upper.color.r * pctUpper),
//         g: Math.floor(lower.color.g * pctLower + upper.color.g * pctUpper),
//         b: Math.floor(lower.color.b * pctLower + upper.color.b * pctUpper)
//     };
//     return 'rgb(' + [color.r, color.g, color.b].join(',') + ')';
//     // or output as hex if preferred
// }

socket.on( 'print message', function( msg ) {
  console.log( msg );
  // msg.comp is the sentiment score normalized from -1 (bad) to +1 (good)
  //TODO: use gradient maybe (low priority)

  if( typeof msg.user_name !== 'undefined' ) {
    if (msg.message != "") {
      style = "background-color: #EFEDE3";
      // if (msg.comp > 0.05) {
      //   style = "background-color: #EFEDE3";
      // }
      // else if (msg.comp < -0.05) {
      //   style = "background-color: #EFEDE3";
      // }
      if (msg.user_name == username) {
        // if you sent this message
        // Appends HTML to DOM
        $('#chat-history').append("<div class='row justify-content-end'><div class='d-inline'><span class='col-auto px-2 pt-0' style='color: #a8aab1; font-size: 80%'>"+msg.time_stamp+"</span><span class='far fa-user-circle' style='color: #86BB71'></span><span class='col-auto px-0 pt-0' style='color: #434651; font-size: 100%'> "+msg.user_name+"</span></div></div><div class='row justify-content-end mb-3'><div class='col-2'></div><div class='col-auto text-left rounded p-2' style='max-width: 70%; display: inline-block;"+style+"'>"+msg.message+"</div></div>");
      } else {
        // Appends HTML to DOM
        $('#chat-history').append("<div class='row justify-content-start d-inline'><span class='far fa-user-circle' style='color: #94C2ED'></span><span class='col-auto px-0 pt-0' style='color: #434651; font-size: 100%'> "+msg.user_name+"</span><span class='col-auto px-2 pt-0' style='color: #a8aab1; font-size: 80%'>"+msg.time_stamp+"</span></div><div class='row justify-content-start mb-3'><div class='col-auto text-left rounded p-2' style='max-width: 70%; display: inline-block;"+style+"'>"+msg.message+"</div><div class='col-2'></div></div>");
      }
      // socket.emit('update graph');
      $('#chat-wrapper').animate({scrollTop: $('#chat-wrapper').prop("scrollHeight")}, 700);
    }
  }
})

socket.on('impolite message', function( msg ){
  impolite_message = msg;
  console.log(msg);
  if( typeof msg.user_name != 'undefined' ) {
    if (msg.message != "") {
      highlighted = highlight(impolite_message);
      $('#impoliteModal').modal('show');//show the modal
    }
  }
})

socket.on('refresh', function(){
  console.log('help')
  window.location.href = "/logout";
});

function getTime(){
  var d = new Date();
  var hr = d.getHours();
  var min = d.getMinutes();
  var ampm = "AM";
  if( hr > 12 ) {
    hr -= 12;
    ampm = "PM";
  }
  if (min < 10) {
    min = "0" + min;
  }
  return hr + ":" + min + " " + ampm;
}
