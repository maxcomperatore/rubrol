package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

type InvoicePayload struct {
	Template    string                 `json:"template"`
	Data        map[string]interface{} `json:"data"`
	Format      string                 `json:"format"`
	PDFStandard string                 `json:"pdf_standard"`
}

func main() {
	url := "http://localhost:8080/v1/render"

	payload := InvoicePayload{
		Template:    "b2b_invoice",
		Format:      "pdf",
		PDFStandard: "a-2b",
		Data: map[string]interface{}{
			"invoice_number":  "INV-2026-GO01",
			"issued_date":     "2026-09-17",
			"due_date":        "2026-10-17",
			"currency":        "USD",
			"currency_symbol": "$",
			"vendor": map[string]string{
				"name":    "Golang High-Concurrency Cluster",
				"tax_id":  "US-991820",
				"address": "Market St",
				"city":    "San Francisco, CA",
				"email":   "go@rubrol.com",
			},
			"customer": map[string]string{
				"name":    "Cloudflare Edge Network",
				"tax_id":  "US-771829",
				"address": "101 Townsend St",
				"city":    "San Francisco, CA",
				"email":   "billing@cloudflare.com",
			},
			"line_items": []map[string]interface{}{
				{
					"description": "Zero-Copy Sidecar Microservice Pod",
					"qty":         1,
					"unit_price":  490.00,
				},
			},
		},
	}

	jsonData, err := json.Marshal(payload)
	if err != nil {
		panic(err)
	}

	start := time.Now()
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		panic(fmt.Sprintf("HTTP %d: %s", resp.StatusCode, string(body)))
	}

	outFile, err := os.Create("go_invoice.pdf")
	if err != nil {
		panic(err)
	}
	defer outFile.Close()

	written, err := io.Copy(outFile, resp.Body)
	if err != nil {
		panic(err)
	}

	renderTime := resp.Header.Get("X-Render-Time-Ms")
	fmt.Printf("Generated go_invoice.pdf (%d bytes) in %v (Engine latency: %sms)
", written, time.Since(start), renderTime)
}
