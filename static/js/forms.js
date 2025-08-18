const code = document.getElementById("id_code");
const name = document.querySelector('input[name="name"]');
const lang = document.querySelector('select[name="lang"]');
const charsCount = document.getElementById("charsCount");

const formDataKey = "draft";

code.addEventListener('input', () => {
    const count = code.value.length;
    let text = `${count}/5000`;
    charsCount.innerHTML = text;
})

function saveDraft(){
    const formData = {
        name: name.value,
        lang: lang.value,
        code: code.value,
    }
    localStorage.setItem(formDataKey, JSON.stringify(formData));
    console.log("form saved");
}

function loadDraft(){
    const data = localStorage.getItem(formDataKey);
    if (!data) return;

    // let restore = confirm("Восстановить данные формы?");
    // if (!restore) return;

    const formData = JSON.parse(data);
    name.value = formData.name;
    lang.value = formData.lang;
    code.value = formData.code;
    console.log("form restored");
}

setInterval(saveDraft, 3000);
document.addEventListener('DOMContentLoaded', loadDraft);