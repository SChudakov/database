$(document).ready(function () {

    $('#save_button').click(function () {

        $.ajax({
            url: '/rest/save',
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
