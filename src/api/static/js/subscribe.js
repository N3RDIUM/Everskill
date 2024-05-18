// If there is not everskill-token and everskill-username in the local storage
if (!localStorage.getItem("everskill-token") && !localStorage.getItem("everskill-username")) {
    window.location.href = '/signin';
}

function askPermission() {
    return new Promise(function (resolve, reject) {
        const permissionResult = Notification.requestPermission(function (result) {
            resolve(result);
        });

        if (permissionResult) {
            permissionResult.then(resolve, reject);
        }
    }).then(function (permissionResult) {
        if (permissionResult !== 'granted') {
            throw new Error("We weren't granted permission.");
        }
    });
}

const pubkey = 'BIuFYQ2xzOaYgq5kHds1WieS8ccvDcvnLot3OHuje-ZzMz4WbiCc0p_1MhIHWLLRZBsebfHPVkk4ixfW9Kwlh9Y';// Get username and token from local storage
let username = localStorage.getItem('everskill-username');
let token = localStorage.getItem('everskill-token');

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

function subscribeUser() {
    return navigator.serviceWorker
        .register('/static/js/service-worker.js')
        .then(async function (registration) {
            const subscribeOptions = {
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(pubkey)
            };
            await navigator.serviceWorker.ready;
            return registration.pushManager.subscribe(subscribeOptions);
        })
        .then(function (pushSubscription) {
            console.log(
                'Received PushSubscription: ',
                JSON.stringify(pushSubscription),
            );
            fetch('/api/subscribe-pushnotify', {
                method: 'POST',
                body: JSON.stringify({
                    username: username,
                    token: token,
                    subscription: JSON.stringify(pushSubscription)
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(async res => {
                let response = await res.json();
                if(!response.success) {
                    alert(response.response);
                }
            });
            return pushSubscription;
        });
}