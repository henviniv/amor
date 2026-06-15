const inicio = new Date("2025-10-27T00:00:00");

function atualizarTempo() {
  const agora = new Date();

  const diff = agora - inicio;

  const dias = Math.floor(diff / (1000 * 60 * 60 * 24));

  document.getElementById("contador").innerHTML = `${dias} dias juntos ❤️`;
}

setInterval(atualizarTempo, 1000);

atualizarTempo();

function abrirFoto(src) {
  const modal = document.getElementById("modal");
  const foto = document.getElementById("fotoAmpliada");

  foto.src = src;
  modal.style.display = "flex";
}

function fecharFoto() {
  document.getElementById("modal").style.display = "none";
}

window.addEventListener("click", function (event) {
  const modal = document.getElementById("modal");

  if (event.target === modal) {
    fecharFoto();
  }
});
