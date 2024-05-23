// Signout
function signout() {
    localStorage.removeItem('everskill-token');
    localStorage.removeItem('everskill-username');
    window.location.href = '/signin/';
}