const code = document.getElementById("id_code");
const charsCount = document.getElementById("charsCount");

code.addEventListener('input', () => {
    const count = code.value.length;
    let text = `${count}/5000`;
    charsCount.innerHTML = text;
})