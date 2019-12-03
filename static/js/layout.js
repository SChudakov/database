$(document).ready(function () {
    const restUrl = "http://127.0.0.1:6000";

    $('#save_button').click(function () {

        $.ajax({
            url: restUrl + '/rest/save',
            type: 'POST',
            success: function (response) {
                console.log(response);
                $('#success_alert').text(response.message).show();
            },
            error: function (error) {
                console.log(error);
                $('#error_alert').text(error.responseJSON.message).show();
            }
        });
    });
});
