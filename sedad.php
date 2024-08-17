<?php
header('Content-Type: application/json');

// Lire les données POST envoyées
$data = json_decode(file_get_contents('php://input'), true);

// Vérifier les données du donneur (exemple simple)
if (isset($data['numero_donneur']) && isset($data['montant'])) {
    $numero_donneur = $data['numero_donneur'];
    $montant = $data['montant'];

    // Simuler la vérification des données
    if ($numero_donneur === '34044505' && $montant > 0) {
        // Réponse de succès
        $response = [
            'status' => 'success',
            'message' => 'Data verified successfully',
        ];
        http_response_code(200);
    } else {
        // Réponse d'erreur
        $response = [
            'status' => 'error',
            'message' => 'Invalid donor data',
        ];
        http_response_code(400);
    }
} else {
    // Réponse d'erreur pour les données manquantes
    $response = [
        'status' => 'error',
        'message' => 'Missing required parameters',
    ];
    http_response_code(400);
}

// Envoyer la réponse JSON
echo json_encode($response);
?>
