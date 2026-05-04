const limitForm = document.querySelector(".limit-form");
const limitInput = document.querySelector("#limit");
const limitValue = document.querySelector("#limit-value");
const chartTypeSelect = document.querySelector("#chart_type");
const browserSelect = document.querySelector("#browser");

function syncControlsFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const limit = params.get("limit");
    const chartType = params.get("chart_type");
    const browser = params.get("browser");

    if (limit && limitInput && limitValue) {
        limitInput.value = limit;
        limitValue.value = limit;
    }

    if (chartType && chartTypeSelect) {
        chartTypeSelect.value = chartType;
    }

    if (browser && browserSelect) {
        browserSelect.value = browser;
    }
}

if (limitForm && limitInput && limitValue) {
    let submitTimer;

    syncControlsFromUrl();
    window.addEventListener("pageshow", syncControlsFromUrl);

    limitInput.addEventListener("input", () => {
        limitValue.value = limitInput.value;
    });

    limitInput.addEventListener("change", () => {
        clearTimeout(submitTimer);
        submitTimer = setTimeout(() => limitForm.requestSubmit(), 200);
    });

    chartTypeSelect?.addEventListener("change", () => {
        limitForm.requestSubmit();
    });

    browserSelect?.addEventListener("change", () => {
        limitForm.requestSubmit();
    });
}
