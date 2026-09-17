// Rubrol C# .NET Client Example
using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

class Program
{
    static async Task Main(string[] args)
    {
        using var client = new HttpClient();
        var url = "http://localhost:8080/v1/render";

        var payload = new
        {
            template = "b2b_invoice",
            format = "pdf",
            pdf_standard = "a-2b",
            data = new
            {
                invoice_number = "INV-2026-NET01",
                issued_date = "2026-09-17",
                due_date = "2026-10-17",
                currency = "USD",
                currency_symbol = "$",
                vendor = new
                {
                    name = "Microsoft Azure ISV Partner",
                    tax_id = "US-9941029",
                    address = "One Microsoft Way",
                    city = "Redmond, WA 98052",
                    email = "billing@partner.com"
                },
                customer = new
                {
                    name = "Contoso Financial Services",
                    tax_id = "US-1192049",
                    address = "100 Wall Street",
                    city = "New York, NY 10005",
                    email = "ap@contoso.com"
                },
                line_items = new[]
                {
                    new
                    {
                        description = "Rubrol Microsecond Sidecar Pod",
                        qty = 1,
                        unit_price = 490.00
                    }
                }
            }
        };

        var json = JsonSerializer.Serialize(payload);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        Console.WriteLine($"Sending render request to {url}...");
        var response = await client.PostAsync(url, content);
        response.EnsureSuccessStatusCode();

        var pdfBytes = await response.Content.ReadAsByteArrayAsync();
        await File.WriteAllBytesAsync("dotnet_invoice.pdf", pdfBytes);

        Console.WriteLine($"Generated dotnet_invoice.pdf ({pdfBytes.Length} bytes)");
    }
}
