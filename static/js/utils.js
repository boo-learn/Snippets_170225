function copyToBuffer(text) {
    navigator.clipboard.writeText(text)
        .then(function () {
            // Этот код выполнится, если промис разрешился (успешное копирование)
            console.log('Текст успешно скопирован!');
        })
        .catch(function (err) {
            // Этот код выполнится, если промис был отклонён (ошибка копирования)
            console.error('Ошибка копирования:', err);
        });
}