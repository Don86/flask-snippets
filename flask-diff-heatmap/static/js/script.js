/* Form not defined yet; unused*/
$(function(){
    $('button').click(function(){
        var user = $('#num1').val();
        var pass = $('#num2').val();
        $.ajax({
            url: '/calc_func',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response){
                console.log(response);
            },
            error: function(error){
                console.log(error);
            }
        });
    });
});