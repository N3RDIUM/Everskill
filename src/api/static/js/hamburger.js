function openNav() {
    document.getElementById("open").style.display = "none";
    document.getElementById("nav").style.width = "100%";
    document.getElementById("nonnav").style.display = "none";
}
function closeNav() {
    document.getElementById("nonnav").style.display = "flex";
    document.getElementById("nav").style.width = "0";
    document.getElementById("open").style.display = "block";
}