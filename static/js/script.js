const showResult = (text) => {
    textAreaElement = document.querySelector('.content-container__result');
    textAreaElement.textContent = text;
};

const sendQuery = async (query, params) => {
    let result = '';
    try {
        if(!query) {
            throw new Error('Empty query');
        }
        const response = await fetch(`${document.location.href}${query}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=UTF-8',
            },
            body: JSON.stringify({
                params: params
            })
        });
        result = await response.text();
    } catch (error) {
        console.log('error send query to server:', error);
    } finally {
        showResult(result);
    }
};

const submitButton = document.getElementById('main-form');
submitButton.addEventListener('submit', (event) => {
    event.preventDefault();
    const { target } = event;
    const inputQueryElement = target.querySelector('.query');
    const inputParamsElement = target.querySelector('.param');
    sendQuery(inputQueryElement?.value, inputParamsElement?.value);
    inputParamsElement.value = '';
});