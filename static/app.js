const limitForm = document.querySelector(".limit-form");
const limitInput = document.querySelector("#limit");
const limitValue = document.querySelector("#limit-value");
const chartTypeSelect = document.querySelector("#chart_type");
const browserSelect = document.querySelector("#browser");
const chartShell = document.querySelector(".chart-shell");

function syncControlsFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const limit = params.get("limit");
    const chartType = params.get("chart_type");
    const browser = params.get("browser");

    if (limit && limitInput && limitValue && Number.isFinite(Number(limit))) {
        limitInput.value = limit;
        limitValue.value = limit;
    }

    if (chartType && chartTypeSelect && hasOption(chartTypeSelect, chartType)) {
        chartTypeSelect.value = chartType;
    }

    if (browser && browserSelect && hasOption(browserSelect, browser)) {
        browserSelect.value = browser;
    }
}

function hasOption(select, value) {
    return Array.from(select.options).some((option) => option.value === value);
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
        submitTimer = setTimeout(submitForm, 200);
    });

    chartTypeSelect?.addEventListener("change", () => {
        submitForm();
    });

    browserSelect?.addEventListener("change", () => {
        submitForm();
    });
}

function submitForm() {
    limitForm.classList.add("is-submitting");
    chartShell?.classList.add("is-changing");
    limitForm.requestSubmit();
}
