$(document).ready(function () {

    // load databases names
    $.ajax({
        url: '/rest/database',
        type: 'GET',
        success: function (response) {
            $.each(response, function (index, name) {
                $('#edit_delete_database_name').append(new Option(name, name))
            })
        },
        error: function (error) {
            console.log(error);
            $('#error_alert').text(error.responseJSON.message).show();
        }
    });


    $('#delete_database').click(function () {

        const database_name = $('#edit_delete_database_name').val();
        const database_url = '/rest/database/' + database_name;

        $.ajax({
            url: database_url,
            type: 'DELETE',
            success: function (response) {
                console.log(response);
                $('#success_alert').text(response.message).show();
                $('option[value=' + database_name + ']').remove()
            },
            error: function (error) {
                console.log(error);
                $('#error_alert').text(error.responseJSON.message).show();
            }
        });
    });

    $('#create_database').click(function () {

        const name = $('#create_database_name').val();
        const database_url = '/rest/database/' + name;

        $.ajax({
            url: database_url,
            type: 'POST',
            success: function (response) {
                console.log(response);
                $('#success_alert').text(response.message).show();
                $('#edit_delete_database_name').append(new Option(name, name))
            },
            error: function (error) {
                console.log(error);
                $('#error_alert').text(error.responseJSON.message).show();
            }
        });
    });

    $('#create_database_form').on('submit', function (event) {
        event.preventDefault();
    });
});