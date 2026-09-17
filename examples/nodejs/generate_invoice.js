// Rubrol Node.js Client Example
// Requires Node 18+ (built-in fetch)
const fs = require('fs');

const RUBROL_URL = 'http://localhost:8080/v1/render';

async function generateInvoice() {
  const payload = {
    template: 'b2b_invoice',
    data: {
      invoice_number: 'INV-2026-NODE01',
      issued_date: '2026-09-17',
      due_date: '2026-10-17',
      currency: 'USD',
      currency_symbol: '$',
      vendor: {
        name: 'Vercel Edge Solutions',
        tax_id: 'US-8819203',
        address: '440 N Barranca Ave',
        city: 'Covina, CA 91723',
        email: 'billing@vercel.com'
      },
      customer: {
        name: 'Supabase Data Labs',
        tax_id: 'US-2291048',
        address: '970 Toa Payoh North',
        city: 'Singapore 318992',
        email: 'accounts@supabase.io'
      },
      line_items: [
        {
          description: 'High-Volume Document Sidecar Worker Pod',
          qty: 2,
          unit_price: 245.00
        }
      ]
    },
    format: 'pdf',
    pdf_standard: 'a-2b'
  };

  console.log(`Sending payload to ${RUBROL_URL}...`);
  const start = Date.now();

  const response = await fetch(RUBROL_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
  }

  const renderTimeMs = response.headers.get('X-Render-Time-Ms');
  const buffer = Buffer.from(await response.arrayBuffer());

  const filename = 'nodejs_invoice.pdf';
  fs.writeFileSync(filename, buffer);

  console.log(`Generated ${filename} (${buffer.length} bytes)`);
  console.log(`Engine Render Latency: ${renderTimeMs}ms | Round-trip: ${Date.now() - start}ms`);
}

generateInvoice().catch(console.error);
