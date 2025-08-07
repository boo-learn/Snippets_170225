const codeCount = document.getElementById('count');
const textArea = document.querySelector('textarea[name="code"]');

const numChars = textArea.value.length;
codeCount.textContent = `${numChars}/5000`;

textArea.addEventListener('input', () => {
    const numChars = textArea.value.length;
    codeCount.textContent = `${numChars}/5000`;
});

// Автосохранение и восстановление черновиков
const STORAGE_KEY = 'snippet_draft';
let autoSaveInterval = null;
const isEditMode = window.location.pathname.includes('edit');

// Инициализация только для создания нового сниппета
if (!isEditMode) {
    console.log("init");
    initDraftManager();
}

function initDraftManager() {
    setupAutoSave();
    checkForDraft();
}

function setupAutoSave() {
    // Автосохранение каждые 10 секунд
    autoSaveInterval = setInterval(() => {
        saveDraft();
        console.log("save");
    }, 2000);

    // Сохранение при изменении полей
    const formFields = document.querySelectorAll('input[name="name"], textarea[name="code"], select[name="lang"]');
    formFields.forEach(field => {
        field.addEventListener('input', () => {
            saveDraft();
        });
    });
}

function saveDraft() {
    const formData = {
        name: document.querySelector('input[name="name"]')?.value || '',
        code: document.querySelector('textarea[name="code"]')?.value || '',
        lang: document.querySelector('select[name="lang"]')?.value || '',
        public: document.querySelector('input[name="public"]')?.checked || false,
        timestamp: new Date().toISOString()
    };

    // Сохраняем только если есть хотя бы одно заполненное поле
    if (formData.name || formData.code) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(formData));
    }
}

function checkForDraft() {
    const savedDraft = localStorage.getItem(STORAGE_KEY);
    if (savedDraft) {
        showRestorePrompt();
    }
    document.querySelector()
}

function showRestorePrompt() {
    const promptDiv = document.createElement('div');
    promptDiv.className = 'alert alert-info alert-dismissible fade show';
    promptDiv.innerHTML = `
        <strong>Найден черновик!</strong> 
        Хотите восстановить сохраненные данные?
        <button type="button" class="btn btn-primary btn-sm ms-2" onclick="restoreDraft()">
            Восстановить черновик
        </button>
        <button type="button" class="btn btn-secondary btn-sm ms-2" onclick="discardDraft()">
            Отменить
        </button>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Вставляем после заголовка
    const titleRow = document.querySelector('.row:first-child');
    titleRow.parentNode.insertBefore(promptDiv, titleRow.nextSibling);
}

function restoreDraft() {
    const savedDraft = localStorage.getItem(STORAGE_KEY);
    if (savedDraft) {
        const draft = JSON.parse(savedDraft);
        
        // Восстанавливаем данные в поля формы
        const nameField = document.querySelector('input[name="name"]');
        const codeField = document.querySelector('textarea[name="code"]');
        const langField = document.querySelector('select[name="lang"]');
        const publicField = document.querySelector('input[name="public"]');

        if (nameField) nameField.value = draft.name || '';
        if (codeField) codeField.value = draft.code || '';
        if (langField) langField.value = draft.lang || '';
        if (publicField) publicField.checked = draft.public || false;

        // Обновляем счетчик символов
        if (codeField && codeCount) {
            const numChars = codeField.value.length;
            codeCount.textContent = `${numChars}/5000`;
        }

        // Удаляем черновик из localStorage
        discardDraft();

        // Показываем уведомление об успешном восстановлении
        showNotification('Черновик успешно восстановлен!', 'success');
    }
}

function discardDraft() {
    localStorage.removeItem(STORAGE_KEY);
    
    // Удаляем prompt если он есть
    const alertElement = document.querySelector('.alert-info');
    if (alertElement) {
        alertElement.remove();
    }
}

function showNotification(message, type = 'info') {
    // Получаем контейнер для уведомлений
    const alertsContainer = document.getElementById('alertsFixedContainer');
    
    if (!alertsContainer) {
        console.error('Контейнер для уведомлений не найден');
        return;
    }

    // Создаем уведомление в общем формате
    const notificationDiv = document.createElement('div');
    notificationDiv.className = `alert alert-${type} alert-dismissible fade show`;
    notificationDiv.setAttribute('role', 'alert');
    notificationDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Закрыть"></button>
    `;

    // Добавляем уведомление в контейнер
    alertsContainer.appendChild(notificationDiv);

    // Автоматически скрываем через 3 секунды
    setTimeout(() => {
        if (notificationDiv.parentNode) {
            notificationDiv.remove();
        }
    }, 3000);
}

function clearDraft() {
    localStorage.removeItem(STORAGE_KEY);
    if (autoSaveInterval) {
        clearInterval(autoSaveInterval);
    }
}

// Очистка черновика при отправке формы
document.querySelector('form').addEventListener('submit', () => {
    clearDraft();
});
