/*
Finds words beginning with a # and surrounds them with a link to the search
page for the entire word.
*/
function createLinksForHashtags(string) {
    return string.replace(/#(\S*)/g, '<a href="/search/wire/$1">#$1</a>');
}


/*
Formats an ISO standard timestamp into "DD/MM/YY at HH:MM".
The timestamp given must be an instance of javascript's Date.

@param timestamp: The timestamp to format as a javascript Date object

@return String: The formatted timestamp
*/
function formatTimeStamp(timestamp) {
    var messageDateString = timestamp.getDate() + "/" + timestamp.getMonth() + "/" + timestamp.getFullYear();
    messageDateString += " at " + timestamp.getHours() + ":" + timestamp.getMinutes();

    return messageDateString;
}

/*
Takes in a username, a button name, and a button type (optional), and
returns HTML output to display the given data in a bootstrap list.
If the button name is 'visit', the button will not be displayed as the
link will be used to visit.

@param username:   The username to display
@param buttonName: The name of the button to display
@param buttonType: The bootstrap class of the button (danger, default, etc.)

@return String: string formatted to be put into a bootstrap list.
*/
function formatUserList(username, buttonName, buttonType = 'default') {
    var userHTML = "";

    userHTML += "<li class='list-group-item clearfix'>";
    userHTML += "<span><a href='/profile/" + username + "/'>" + username + "</a></span>";
    if (buttonName !== 'visit') {
        userHTML += "<span class='pull-right'><a href='#' id='" + buttonName + "-" + username + "' class='btn btn-" + buttonType + " " + buttonName + "-button'>" + buttonName + "</a></span>";
    }
    userHTML += "</li>";

    return userHTML
}
