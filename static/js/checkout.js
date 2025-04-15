async function initiateCheckout() {

    // Determine the page type
    const pageType = document.body.dataset.page;
    const isStartPage = pageType === 'start';

    try {
        const configuration = {
            clientKey: "test_3QQM2ANFMVFDLB5S7YIMWFTSME4FL65Z",
            environment: "test",
            amount: {
                value: 8000,
                currency: 'PLN'
            },
            locale: 'en-US',
            countryCode: 'PL',
            translations: {
                'en-US': {
                    'payButton': 'Buy Now' // Customize the pay button text
                }
            },

            paymentMethodsResponse: await makePaymentMethodsCall(),

            onSubmit: async (state, component, actions) => {
                try {
                    const result = await makePaymentsCall(state.data);

                    if (!result.resultCode) {
                        actions.reject();
                        return;
                    }

                    const {
                        resultCode,
                        action,
                        order,
                        donationToken
                    } = result;

                    actions.resolve({
                        resultCode,
                        action,
                        order,
                        donationToken,
                    });
                } catch (error) {
                    console.error("onSubmit", error);
                    actions.reject();
                }
            },
            onAdditionalDetails: async (state, component, actions) => {
                try {
                    const result = await makeDetailsCall(state.data);

                    if (!result.resultCode) {
                        actions.reject();
                        return;
                    }

                    const {
                        resultCode,
                        action,
                        order,
                        donationToken
                    } = result;

                    actions.resolve({
                        resultCode,
                        action,
                        order,
                        donationToken,
                    });
                } catch (error) {
                    console.error("onAdditionalDetails", error);
                    actions.reject();
                }
            },
            onPaymentCompleted: (result, component) => {
                console.info('onPaymentCompleted triggred', result, component);
            },
            onPaymentFailed: (result, component) => {
                console.info('on payment failed triggered', result, component);
            },
            onError: (error, component) => {
                console.error('onError triggered',error.name, error.message, error.stack, component);
            }
        }; 

        //custom configurations
        const dropInConfiguration = {
            showPaymentMethods: !isStartPage, //if false only stored method will display 
            showStoredPaymentMethods:isStartPage, 
            openFirstPaymentMethod:false,
            paymentMethodsConfiguration: {
                card: {                       //https://docs.adyen.com/payment-methods/cards/web-drop-in/#optional-configuration
                    hasHolderName: true,
                    holderNameRequired: true,
                    billingAddressRequired: false,
                    enableStoreDetails:true

                },
                storedCard: {
                    hideCVC: true
                }
            }
        }
        

        const checkout = await AdyenWeb.AdyenCheckout(configuration);
        const dropin = new AdyenWeb.Dropin(checkout, dropInConfiguration).mount('#dropin');
    } catch (error) {
        console.error(error);
    }
}

function handleServerResponse(response, dropin) {
    if (response.action) {
        dropin.handleAction(response.action);
    } else {
        switch (response.resultCode) {
            case 'Authorised':
                window.location.href = '/result/success';
                break;
            case 'Pending':
            case 'Received':
                window.location.href = '/result/pending';
                break;
            case 'Refused':
                window.location.href = '/result/failed';
                break;
            default:
                window.location.href = '/result/error';
                break;
        }
    }
}

async function makePaymentMethodsCall(data = {}) {
    return await callServer('/paymentMethods', data);
}

async function makePaymentsCall(data) {
    return await callServer('/payments', data);
}

async function makeDetailsCall(data) {
    return await callServer('/payments/details', data);
}

async function callServer(endpoint, data) {
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server error (${response.status}): ${errorText}`);
    }
    return await response.json();
}

initiateCheckout();