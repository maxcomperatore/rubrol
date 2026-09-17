use serde_json::json;
use std::fs::File;
use std::io::Write;
use std::time::Instant;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = reqwest::blocking::Client::new();
    let url = "http://localhost:8080/v1/render";

    let payload = json!({
        "template": "b2b_invoice",
        "format": "pdf",
        "pdf_standard": "a-2b",
        "data": {
            "invoice_number": "INV-2026-RS01",
            "issued_date": "2026-09-17",
            "due_date": "2026-10-17",
            "currency": "USD",
            "currency_symbol": "$",
            "vendor": {
                "name": "Rust Systems Corp",
                "tax_id": "US-991824",
                "address": "123 Memory Safe Way",
                "city": "Seattle, WA",
                "email": "rust@rubrol.com"
            },
            "customer": {
                "name": "Fastly Edge Compute",
                "tax_id": "US-440192",
                "address": "475 Brannan St",
                "city": "San Francisco, CA",
                "email": "finance@fastly.com"
            },
            "line_items": [
                {
                    "description": "Zero-Memory-Leak Typst Sidecar Engine",
                    "qty": 1,
                    "unit_price": 490.00
                }
            ]
        }
    });

    println!("Sending render request to {}...", url);
    let start = Instant::now();

    let resp = client.post(url)
        .header("Content-Type", "application/json")
        .json(&payload)
        .send()?;

    let render_time = resp.headers()
        .get("X-Render-Time-Ms")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("N/A")
        .to_string();

    let bytes = resp.bytes()?;
    let mut file = File::create("rust_invoice.pdf")?;
    file.write_all(&bytes)?;

    println!("Success! Wrote {} bytes to rust_invoice.pdf in {:.2?} (Sidecar compile: {}ms)",
        bytes.len(), start.elapsed(), render_time
    );

    Ok(())
}
