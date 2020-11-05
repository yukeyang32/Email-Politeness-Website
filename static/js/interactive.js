function mark_politeness(elem,indices, strats) {
    var j;
    for(j = 0; j < indices.length; j++) {
        var i = indices[j].toString();
        var id = '#'.concat(i);
        $(id).css('background-color','rgba(4, 169, 180, 0.596)');
        $(elem).css('background-color','rgba(4, 169, 180, 0.596)');
    }
    var clicked = $(elem).attr("id");
    if(clicked == "hasnegative") {
        if(jQuery.inArray('Please start',strats) != -1) {
            $('#please-start').css('background-color','white');
        }
        if(jQuery.inArray('2nd person start',strats) != -1) {
            $('#2nd-person-start').css('background-color','white');
        }
        if(jQuery.inArray('Direct question',strats) != -1) {
            $('#direct-question').css('background-color','white');
        }
        $('.strat-info').html('Your message contains words that may be interpreted as hurtful and/or unconstructive.'.concat(
            ' Try rewording your message by removing the negative words.<br/><br/>',
            '<strong>Example: </strong>If your message is “You are a terrible friend”, where “terrible” is the negative word, you may want to reword it to: “I do not think you have been a good friend lately. Can we talk about it?”'));
    }
    else if(clicked == "please-start") {
        if(jQuery.inArray('HASNEGATIVE',strats) != -1) {
            $('#hasnegative').css('background-color','white');
        }
        if(jQuery.inArray('2nd person start',strats) != -1) {
            $('#2nd-person-start').css('background-color','white');
        }
        if(jQuery.inArray('Direct question',strats) != -1) {
            $('#direct-question').css('background-color','white');
        }
        $('.strat-info').html('Your message contains at least one sentence that starts with “please,” which may be interpreted as demanding and/or unconstructive.'.concat(
            ' Try adding a contextual sentence beforehand or changing the sentence into a question, if applicable.<br/><br/>',
        '<strong>Example: </strong>If your message is “Please complete your part of the project.” You may want to reword it to: “I noticed that you haven’t completed your part of the project yet. Can you please complete it as soon as you can?”'));
    }
    else if(clicked == "2nd-person-start") {
        if(jQuery.inArray('HASNEGATIVE',strats) != -1) {
            $('#hasnegative').css('background-color','white');
        }
        if(jQuery.inArray('Please start',strats) != -1) {
            $('#please-start').css('background-color','white');
        }
        if(jQuery.inArray('Direct question',strats) != -1) {
            $('#direct-question').css('background-color','white');s
        }
        $('.strat-info').html('Your message contains at least one sentence that begins in 2nd person. Beginning a sentence with second person can often be interpreted as demanding.'.concat(
            ' Try using “I” statements, providing context before addressing the recipient directly and/or rewording the message into a question, if applicable.<br/><br/>',
        '<strong>Example: </strong>If your message is “You should call the client.” You may want to reword it to: “I am a bit busy right now; can you call the client instead?”'));
    }
    else {
        if(jQuery.inArray('HASNEGATIVE',strats) != -1) {
            $('#hasnegative').css('background-color','white');
        }
        if(jQuery.inArray('2nd person start',strats) != -1) {
            $('#2nd-person-start').css('background-color','white');
        }
        if(jQuery.inArray('Please start',strats) != -1) {
            $('#pleast-start').css('background-color','white');
        }
        $('.strat-info').html('Your message contains at least one direct question, which may be interpreted as forward or blunt.'.concat(
            ' Try adding a contextual sentence beforehand to lessen the forwardness of your message.<br/><br/>',
        '<strong>Example:</strong> If your message is “Can you print out the assignment?” You may want to reword it to: “My printer broke, so I am unable to print the assignment. Can you print out the assignment instead?”'));
    }
}