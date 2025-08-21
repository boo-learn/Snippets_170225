/**
 * Long Polling для уведомлений
 * Отправляет запрос на api/notifications/unread-count/ и ждет ответа
 * Сервер отвечает только если есть непрочитанные уведомления
 */

// Глобальные переменные для состояния
let isPolling = false;
let pollingInterval = null;
let notificationCounter = document.getElementById('notification-count');
let lastCount = 0;
let isAuth = document.getElementById('isAuth').innerHTML; // 'true'/'false'

console.log(`isAuth=${isAuth}`);

const BASE_URL = '/api/notifications/unread-count/';

// Функция для запуска polling
function startPolling() {
    if (isAuth === 'false') return;
    if (isPolling) return;
    isPolling = true;
    poll();
}

// Основная функция polling с использованием промисов
function poll() {
    if (!isPolling) return;
    console.log("start polling!!!");
    // Создаем промис для fetch запроса
    fetch(`${BASE_URL}?last_count=${lastCount}`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        },
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
                notificationCounter.textContent = data.unread_count;
                lastCount = data.unread_count;
            }
        })
        .catch(function (error) {
            console.error('Ошибка при получении уведомлений:', error);
        })
        .finally(function () {
            // Продолжаем polling
            if (isPolling) {
                pollingInterval = setTimeout(function () {
                    poll();
                }, 1000);
            }
        });
}

document.addEventListener('DOMContentLoaded', function () {
    startPolling();
});