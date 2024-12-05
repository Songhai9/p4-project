# Définit la variable pour le répertoire de travail actuel
$PWD = (Get-Location).Path

# Exécute Docker avec bash et des options similaires à celles du script Bash d'origine
docker run --rm -it --privileged `
    -v "${PWD}:/home" `
    registry.app.unistra.fr/jr.luttringer/reseaux-programmables-conteneur/p4-utils `
