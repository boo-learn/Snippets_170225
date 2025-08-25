function voteComment(event, commentId, vote) {
    event.preventDefault();
    fetch('/api/comment/like', {
        method: 'POST', headers: {
            'Accept': 'application/json', 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }, body: JSON.stringify({
            comment_id: commentId, vote: vote
        })
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
                let likesCount = data.likes_count;
                let dislikesCount = data.dislikes_count;
                {
                    let parentComment = document.getElementById(commentId);
                    let likeElement = parentComment.querySelector(".badge.bg-success");
                    let dislikeElement = parentComment.querySelector(".badge.bg-danger");
                    likeElement.innerHTML = likesCount;
                    dislikeElement.innerHTML = dislikesCount;
                }
            }
        })
        .catch(function (error) {
            console.error('Ошибка при получении уведомлений:', error);
        });
}