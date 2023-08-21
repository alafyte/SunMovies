chosenSeats = [];

$('.seats-container').on('click', 'input:checkbox', function () {
    $(this).parent().toggleClass('chosenSeat', this.checked);
    this.checked ? chosenSeats.push(this) : chosenSeats.splice(chosenSeats.indexOf(this), 1);

    let button = $("#order-button");
    chosenSeats.length !== 0 ? button.prop("disabled", false) : button.prop("disabled", true);
    console.log(chosenSeats)
});