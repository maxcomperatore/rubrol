// Rubrol TypeScript Client Example
import * as fs from 'fs';

interface InvoiceData {
  invoice_number: string;
  issued_date: string;
  due_date: string;
  currency: string;
  currency_symbol: string;
  vendor: {
    name: string;
    tax_id: string;
    address: string;
    city: string;
    email: string;
  };
  customer: {
    name: string;
    tax_id: string;
    address: string;
    city: string;
    email: string;
  };
  line_items: Array<{
    description: string;
    qty: number;
    unit_price: number;
  }>;
}

interface RenderRequest {
  template: string;
  data: InvoiceData;
  format: 'pdf' | 'svg';
  pdf_standard?: 'a-2b' | 'a-3b';
}

async function run() {
  const requestBody: RenderRequest = {
    template: 'b2b_invoice',
    format: 'pdf',
    pdf_standard: 'a-2b',
    data: {
      invoice_number: 'INV-2026-TS01',
      issued_date: '2026-09-17',
      due_date: '2026-10-17',
      currency: 'USD',
      currency_symbol: '$',
      vendor: {
        name: 'Rubrol Core Europe',
        tax_id: 'FR82982391820',
        address: '10 Rue de la Paix',
        city: '75002 Paris, France',
        email: 'billing@rubrol.com'
      },
      customer: {
        name: 'Enterprise FinTech AG',
        tax_id: 'DE391820491',
        address: 'Taunusanlage 8',
        city: '60329 Frankfurt am Main, Germany',
        email: 'invoicing@fintech.de'
      },
      line_items: [
        {
          description: 'Rubrol Pro Template Vault License',
          qty: 1,
          unit_price: 490.00
        }
      ]
    }
  };

  const res = await fetch('http://localhost:8080/v1/render', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody)
  });

  if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
  const pdfBytes = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync('typescript_invoice.pdf', pdfBytes);
  console.log(`Successfully compiled typescript_invoice.pdf (${pdfBytes.length} bytes)`);
}

run();
