const inicio = new Date("2025-10-27T00:00:00");

function atualizarTempo() {
  const agora = new Date();

  const diff = agora - inicio;

  const dias = Math.floor(diff / (1000 * 60 * 60 * 24));

  document.getElementById("contador").innerHTML = `${dias} dias juntos ❤️`;
}

setInterval(atualizarTempo, 1000);

atualizarTempo();
