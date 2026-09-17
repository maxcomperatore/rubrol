<?php
// Rubrol PHP Client Example

$url = 'http://localhost:8080/v1/render';

$payload = [
    'template' => 'b2b_invoice',
    'format' => 'pdf',
    'pdf_standard' => 'a-2b',
    'data' => [
        'invoice_number' => 'INV-2026-PHP01',
        'issued_date' => '2026-09-17',
        'due_date' => '2026-10-17',
        'currency' => 'EUR',
        'currency_symbol' => '€',
        'vendor' => [
            'name' => 'Rubrol Europe SAS',
            'tax_id' => 'FR82982391820',
            'address' => '10 Rue de la Paix',
            'city' => '75002 Paris',
            'email' => 'billing@rubrol.com'
        ],
        'customer' => [
            'name' => 'Laravel Cloud Enterprise',
            'tax_id' => 'NL89201948',
            'address' => 'Keizersgracht 421',
            'city' => '1016 EK Amsterdam',
            'email' => 'billing@laravel.com'
        ],
        'line_items' => [
            [
                'description' => 'Rubrol Sidecar Cluster License',
                'qty' => 1,
                'unit_price' => 490.00
            ]
        ]
    ]
];

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_HEADER, true);

$response = curl_exec($ch);
$header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
$headers = substr($response, 0, $header_size);
$body = substr($response, $header_size);
curl_close($ch);

file_put_contents('php_invoice.pdf', $body);
echo "Generated php_invoice.pdf (" . strlen($body) . " bytes)
";
?>
