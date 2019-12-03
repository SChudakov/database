$(document).ready(function () {
    const restUrl = "http://127.0.0.1:6000";


    function getRowId(rowId) {
        return 'row-' + rowId;
    }

    function appendRow(row) {
        var table_row = [];
        table_row.push('<tr id="' + getRowId(row.id) + '">');
        table_row.push('<td>');
        table_row.push(row.id);
        table_row.push('</td>');
        $.each(row.data, function (index, datum) {
            table_row.push('<td>');
            table_row.push(datum);
            table_row.push('</td>')
        });
        table_row.push('</tr>');
        $('#table tbody').append(table_row.join(''))
    }

    $.ajax({
        url: restUrl + '/rest' + window.location.pathname,
        type: 'GET',
        success: function (response) {
            console.log(response);

            var headRow = [];
            headRow.push('<tr>');
            headRow.push('<th scope="col">');
            headRow.push('id');
            headRow.push('</th>');
            for (var i = 0; i < response.column_names.length; ++i) {
                console.log(i);
                headRow.push('<th scope="col">');
                headRow.push(response.column_names[i]);
                headRow.push(':');
                headRow.push(response.columns_types[i]);
                headRow.push('</th>');
            }
            headRow.push('</tr>');
            $('#table thead').append(headRow.join(''));

            $.each(response.rows, function (index, row) {
                appendRow(row)
            });
        },
        error: function (error) {
            console.log(error);
            $('#error_alert').text(error.responseJSON.message).show();
        }
    });

    $('#create_row').click(function () {
        const row_data = $('#create_row_data').val();

        $.ajax({
            url: restUrl + '/rest' + window.location.pathname + '/row?row_data\=' + row_data,
            type: 'POST',
            success: function (response) {
                console.log(response);
                $('#success_alert').text(response.message).show();
                appendRow(response.row);
            },
            error: function (error) {
                console.log(error);
                $('#error_alert').text(error.responseJSON.message).show();
            }
        });
    });

    $('#delete_row').click(function () {
        const row_id = $('#delete_row_id').val();

        $.ajax({
            url: restUrl + '/rest' + window.location.pathname + '/row?row_id\=' + row_id,
            type: 'DELETE',
            success: function (response) {
                console.log(response);
                $('#success_alert').text(response.message).show();
                $('#' + getRowId(response.row.id)).remove()
            },
            error: function (error) {
                console.log(error);
                $('#error_alert').text(error.responseJSON.message).show();
            }
        });
    });


    $('#create_row_form').on('submit', function (event) {
        event.preventDefault();
    });

    $('#update_row_form_div').remove();

    $('#delete_row_form').on('submit', function (event) {
        event.preventDefault();
    });
});