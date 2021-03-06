function submit_message(message) {
        // retrieve response(data) from route(message) by callback
        $.post( "/send_message", {message: message}, handle_response);

        function handle_response(data) {

          // append the bot repsonse to the div
          $('.chat-container').append(`
                <div class="chat-message col-md-5 offset-md-7 bot-message">
                    ${data.message}
                </div>
          `)
          // remove the loading indicator
          $( "#loading" ).remove();
        }
    }


$('#target').on('submit', function(e){
        e.preventDefault();
        // fetch message from input-box
        const input_message = $('#input_message').val()

        // return if the user does not enter any text
        if (!input_message) {
          return
        }

        // add input to customer balloon
        $('.chat-container').append(`
            <div class="chat-message col-md-5 human-message">
                ${input_message}
            </div>
        `)

        // add loading ...  to bot balloon
        $('.chat-container').append(`
            <div class="chat-message text-center col-md-2 offset-md-10 bot-message" id="loading">
                <b>...</b>
            </div>
        `)

        // scroll down - keep last message in view
        //$('.chat-container').animate({scrollTop: 1});
        $('.chat-container').scrollTop($('.chat-container')[0].scrollHeight - $('.chat-container')[0].clientHeight);

        // clear the text input from input-box
        $('#input_message').val('')

        // send the message
        submit_message(input_message)
    });
