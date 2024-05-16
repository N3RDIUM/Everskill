function receivePushNotification(event) {
    var options = JSON.parse(event.data.text());
    event.waitUntil(self.registration.showNotification(options.title, options));
}
self.addEventListener("push", receivePushNotification);
