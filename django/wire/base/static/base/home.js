$(document).ready(function() {
    $('.messages-list .list-group-item .list-group-item-heading').each(function() {
        $(this).html(createLinksForHashtags($(this).text()));
    })
});
