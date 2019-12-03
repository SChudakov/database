$(document).ready(function () {
    const restUrl = "http://127.0.0.1:6000";

    // load table names
    $.ajax({
        url: restUrl + '/rest' + window.location.pathname + '/table',
        type: 'GET',
        success: function (response) {
            $.each(response, function (index, name) {
                $('#edit_delete_table_name').append(new Option(name, name))
            });
        },
        error: function (error) {
            console.log(error);
            $('#error_alert').text(error.responseJSON.message).show();
        }
    });

    $('#delete_table').click(function () {
        const table_name = $('#edit_delete_table_name').val();

        $.ajax({
            url: restUrl + '/rest' + window.location.pathname + '/table/' + table_name,
            type: 'DELETE',
            success: function (response) {
                console.log(response);
                $('#success_alert').text(response.message).show();
                $('option[value=' + table_name + ']').remove()
            },
            error: function (error) {
                console.log(error);
                $('#error_alert').text(error.responseJSON.message).show();
            }
        });
    });

    $('#create_table').click(function () {

        const name = $('#create_table_name').val();
        const sql = $('#columns_info').val();


        $.post(
            restUrl + "/rest" + window.location.pathname + "/table/" + name + "?sql\=" + sql,
        ).done(function (response) {
                console.log(response);
                $('#success_alert').text(response.message).show();
                $('#edit_delete_table_name').append(new Option(name, name))
            }
        ).fail(function (error) {
            console.log(error);
            $('#error_alert').text(error.responseJSON.message).show();
        });
    });

    $('#create_table_form').on('submit', function (event) {
        event.preventDefault();
    });

    $('#join_tables_form_div').remove();
});