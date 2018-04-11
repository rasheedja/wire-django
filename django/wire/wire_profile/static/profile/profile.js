$(document).ready(function() {

    /*
    Formats each message into HTML to be shown on the frontend and then displays the message.

    @param message:           The contents of the message
    @param messageDateString: Date and time as a string
    */
    function formatMessage(message, messageDateString) {
        var formattedMessage = createLinksForHashtags(message);
        var messagesList = $("#messages-list");
        var messagesHtml = "<li class='list-group-item'>";
        messagesHtml += "<h4 class='list-group-item-heading'>" + formattedMessage + "</h4>";
        messagesHtml += "<p class='list-group-item-text'>";
        messagesHtml += "Posted on " + messageDateString;
        messagesHtml += "</p>";
        messagesHtml += "</li>";

        $('.user-wires .loader-container').remove()
        messagesList.append(messagesHtml);
    }

    // Load all messages posted by followers using AJAX
    function loadMessages() {
        $.ajax(
            {
                url: "/message/".concat(jsUsername),
                type: "GET",
                success: function (result) {
                    var messagesHeader = $("#messages-header");
                    // Display a message if the user has not posted any messages
                    if (result.length === 0) {
                        messagesHeader.nextAll('li').remove();
                        messagesHeader.after("<li class='list-group-item'>This user has not created any wires</li>");
                    } else {
                        // Display messages if we received a result from the server
                        $.each(result, function(index, messageObject) {
                            // Format the date from the message to
                            var messageDate = new Date(messageObject.created);
                            var messageDateString = formatTimeStamp(messageDate);

                            formatMessage(messageObject.message_text, messageDateString, messageObject.user);
                        });
                    }
                }
            }
        )
    }

    /*
    Load users not followed by the currently logged in user or, if user is
    not logged in, load some random users.
    */
    function loadRecommendedUsers() {
        // Retrieve other users to display on the frontend
        $.ajax(
            {
                url: "/get-recommended-users/".concat(jsUsername),
                type: "GET",
                success: function (result) {
                    var usersHTML = "";
                    var recommendedUsersHeader = $("#recommended-users-header");

                    result.forEach(function(userObject) {
                        usersHTML += formatUserList(userObject.username, "visit");
                    });

                    if (usersHTML === "") {
                        usersHTML += "<li class='list-group-item clearfix'>";
                        usersHTML += "<span>There are no users to recommend at this time</span>";
                        usersHTML += "</li>";
                    }

                    recommendedUsersHeader.nextAll('li').remove();
                    recommendedUsersHeader.after(usersHTML);

                    $('.follow-button').click(function() {
                        var element = this;
                        var username = element.id.split('-')[1];

                        $.ajax(
                            {
                                url: "/follow/" + username + "/",
                                types: "GET",
                                success: function (result) {
                                    element.classList.add('btn-success');
                                    element.classList.add('disabled');
                                    element.innerHTML = '<span class="glyphicon glyphicon-ok-circle"></span>';
                                    loadRecommendedUsers();
                                    // loadFollows();
                                }
                            }
                        )
                    })
                }
            }
        )
    }


    // /*
    // Load users who are being followed by the user whose profile page is being viewed
    // */
    // function loadFollows() {
    //     $.ajax(
    //         {
    //             url: "@{FollowingR username}",
    //             type: "GET",
    //             success: function (result) {
    //                 if (!result.success && result.success !== undefined) {
    //                     console.log(result.message)
    //                 } else {
    //                     var usersHTML = "";
    //                     var followingHeader = $("#following-header");
    //
    //                     if (result.length !== 0) {
    //                         // Store following user Ids in an array
    //                         var followingUserIds = [];
    //                         result.forEach(function (followInfo) {
    //                             followingUserIds.push(followInfo.followingId);
    //                         });
    //
    //                         $.ajax(
    //                             {
    //                                 url: "/users/" + followingUserIds.join('/'),
    //                                 type: "GET",
    //                                 success: function (result) {
    //                                     result.forEach(function (userObject) {
    //                                         usersHTML += formatUserList(userObject.username, "visit");
    //                                     });
    //
    //                                     followingHeader.nextAll('li').remove();
    //                                     followingHeader.after(usersHTML);
    //
    //                                     $('.unfollow-button').click(function() {
    //                                         var element = this;
    //                                         var username = element.id.split('-')[1];
    //
    //                                         $.ajax(
    //                                             {
    //                                                 url: "/follow/" + username + "/",
    //                                                 types: "GET",
    //                                                 success: function (result) {
    //                                                     console.log(result);
    //                                                     console.log(element);
    //                                                     element.classList.add('btn-success');
    //                                                     element.classList.add('disabled');
    //                                                     element.innerHTML = '<span class="glyphicon glyphicon-ok-circle"></span>'
    //                                                     loadRecommendedUsers();
    //                                                     loadFollows();
    //                                                 }
    //                                             }
    //                                         )
    //                                     })
    //                                 }
    //                             }
    //                         )
    //                     } else {
    //                         usersHTML += "<li class='list-group-item clearfix'>";
    //                         usersHTML += "<span>This user is not following anyone</span>";
    //                         usersHTML += "</li>";
    //
    //                         followingHeader.nextAll('li').remove();
    //                         followingHeader.after(usersHTML);
    //                     }
    //                 }
    //             }
    //         }
    //     )
    // }

    // /*
    // Load users following the person whose profile page is being viewed.
    // */
    // function loadFollowers() {
    //     $.ajax(
    //         {
    //             url: "@{FollowersR username}",
    //             type: "GET",
    //             success: function (result) {
    //                 if (!result.success && result.success !== undefined) {
    //                     console.log(result.message)
    //                 } else {
    //                     var followersHeader = $("#followers-header");
    //                     var usersHTML = "";
    //
    //                     if (result.length !== 0) {
    //                         // Store follower user Ids in an array
    //                         var followerUserIds = [];
    //                         result.forEach(function (followInfo) {
    //                             followerUserIds.push(followInfo.followerId);
    //                         });
    //
    //                         $.ajax(
    //                             {
    //                                 url: "/users/" + followerUserIds.join('/'),
    //                                 type: "GET",
    //                                 success: function (result) {
    //                                     result.forEach(function (userObject) {
    //                                         usersHTML += formatUserList(userObject.username, "visit", "default");
    //                                     });
    //
    //                                     followersHeader.nextAll('li').remove();
    //                                     followersHeader.after(usersHTML);
    //                                 }
    //                             }
    //                         )
    //                     } else {
    //                         usersHTML += "<li class='list-group-item clearfix'>";
    //                         usersHTML += "<span>This user does not have any followers</span>";
    //                         usersHTML += "</li>";
    //
    //                         followersHeader.nextAll('li').remove();
    //                         followersHeader.after(usersHTML);
    //                     }
    //                 }
    //             }
    //         }
    //     )
    // }

    loadMessages();
    loadRecommendedUsers();
    // loadFollows();
    // loadFollowers();
});