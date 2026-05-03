const limitForm = document.querySelector(".limit-form");
const limitInput = document.querySelector("#limit");
const limitValue = document.querySelector("#limit-value");

if (limitForm && limitInput && limitValue) {
    let submitTimer;

    limitInput.addEventListener("input", () => {
        limitValue.value = limitInput.value;
    });

    limitInput.addEventListener("change", () => {
        clearTimeout(submitTimer);
        submitTimer = setTimeout(() => limitForm.requestSubmit(), 200);
    });
}
