$(document).ready(function() {

	alert("Hello")

	$('.post').click( function() {

		alert("Hello")

		var name  = $('#name').val()
		var email = $('#email').val()
		var password = $('#password').val()
		var product = $('#product').val()
		var review = $('#message').val()

		var msg = "<tr><td>" + name + "</td><td>"+product+"</td><td>"+review+"</td></tr>"

		$('#historyReviews').append(msg)

	});

});


