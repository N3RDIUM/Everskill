function receivePushNotification(event) {
    console.log("[Service Worker] Push Received.", event.data);
    var options = {
        body:  event.data.text()
    };
    event.waitUntil(self.registration.showNotification("Everskill", options));
}
self.addEventListener("push", receivePushNotification);
