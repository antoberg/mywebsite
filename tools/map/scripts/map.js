document.getElementById("read_gpx_btn").addEventListener("click", function() {
    fetch('/read-gpx', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({message: "Bonjour depuis le JS"})
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        alert(data.message);  // Optionnel : Affiche un message lorsque la fonction est déclenchée
    })
    .catch(error => console.error('Erreur:', error));
});
