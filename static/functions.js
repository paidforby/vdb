function start_long_task() {
       // add task status elements 
       div = $('<div class="progress"><div></div><div>0%</div><div>...</div><div>&nbsp;</div></div><hr>');
       $('#progress').append(div);
       var video_url = encodeURIComponent($('#link').val());
        //encodeURIComponent(
       //var parts = video_url.split('/') 
       //var video_id = /[^/]*$/.exec(video_url)[0];
       var url = '/ytdl?url=' + video_url;

       // create a progress bar
       var nanobar = new Nanobar({
           bg: '#44f',
           target: div[0].childNodes[0]
       });

       // send ajax POST request to start background job
       $.ajax({
           type: 'POST',
           url: url,
           success: function(data, status, request) {
               status_url = request.getResponseHeader('Location');
               update_progress(status_url, nanobar, div[0]);
           },
           error: function() {
               alert('Unexpected error');
           }
       });
   }

function update_progress(status_url, nanobar, status_div) {
      // send GET request to status URL
      var result
      $.getJSON(status_url, function(data) {
          // update UI
          percent = parseInt(data['current'] * 100 / data['total']);
          nanobar.go(percent);
          $(status_div.childNodes[1]).text(percent + '%');
          $(status_div.childNodes[2]).text(data['status']);
          if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
              if ('result' in data) {
                  // show result
                  $(status_div.childNodes[3]).text('Result: ' + data['result']);
                  window.location.href = '/download?title='+ data['result'];
              }
              else {
                  // something unexpected happened
                  $(status_div.childNodes[3]).text('Result: ' + data['state']);
              }
          }
          else {
              // rerun in 2 seconds
              setTimeout(function() {
                  update_progress(status_url, nanobar, status_div);
              }, 2000);
          }
      });
  }

$(function() {
            $('#download').click(start_long_task);
        });