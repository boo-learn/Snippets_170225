const messagesContainer = document.getElementById("alertsFixedContainer");
const messages = messagesContainer.querySelectorAll('div');

function deleteMessage(message){
    message.remove();
}


function deleteMessages(){
    let step = 800;
    let numMessage = 0;
    for (let message of messages){
        setTimeout(deleteMessage, 3000 + step * numMessage, message);
        numMessage++;
    }
}

deleteMessages();