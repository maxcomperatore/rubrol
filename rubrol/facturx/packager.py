"""
Rubrol Factur-X / ZUGFeRD PDF/A-3b Packager.
Embeds UN/CEFACT CII XML (factur-x.xml) into a PDF/A-3b container with full
Associated Files (/AF), /AFRelationship /Alternative, and ISO 19005-3 XMP metadata.
"""
import datetime
import io
import re
from typing import Optional, Union
import pypdf
from pypdf.generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    IndirectObject,
    NameObject,
    create_string_object,
)

FACTURX_XMP_EXTENSION_SCHEMA = """
    <rdf:Description xmlns:pdfaExtension="http://www.aiim.org/pdfa/ns/extension/"
                     xmlns:pdfaSchema="http://www.aiim.org/pdfa/ns/schema#"
                     xmlns:pdfaProperty="http://www.aiim.org/pdfa/ns/property#"
                     rdf:about="">
      <pdfaExtension:schemas>
        <rdf:Bag>
          <rdf:li rdf:parseType="Resource">
            <pdfaSchema:schema>Factur-X PDFA Extension Schema</pdfaSchema:schema>
            <pdfaSchema:namespaceURI>urn:factur-x:pdfa:CrossIndustryDocument:invoice:1p0#</pdfaSchema:namespaceURI>
            <pdfaSchema:prefix>fx</pdfaSchema:prefix>
            <pdfaSchema:property>
              <rdf:Seq>
                <rdf:li rdf:parseType="Resource">
                  <pdfaProperty:name>DocumentFileName</pdfaProperty:name>
                  <pdfaProperty:valueType>Text</pdfaProperty:valueType>
                  <pdfaProperty:category>external</pdfaProperty:category>
                  <pdfaProperty:description>The name of the embedded XML document</pdfaProperty:description>
                </rdf:li>
                <rdf:li rdf:parseType="Resource">
                  <pdfaProperty:name>DocumentType</pdfaProperty:name>
                  <pdfaProperty:valueType>Text</pdfaProperty:valueType>
                  <pdfaProperty:category>external</pdfaProperty:category>
                  <pdfaProperty:description>The type of the hybrid document in capital letters</pdfaProperty:description>
                </rdf:li>
                <rdf:li rdf:parseType="Resource">
                  <pdfaProperty:name>Version</pdfaProperty:name>
                  <pdfaProperty:valueType>Text</pdfaProperty:valueType>
                  <pdfaProperty:category>external</pdfaProperty:category>
                  <pdfaProperty:description>The actual version of the Factur-X schema</pdfaProperty:description>
                </rdf:li>
                <rdf:li rdf:parseType="Resource">
                  <pdfaProperty:name>ConformanceLevel</pdfaProperty:name>
                  <pdfaProperty:valueType>Text</pdfaProperty:valueType>
                  <pdfaProperty:category>external</pdfaProperty:category>
                  <pdfaProperty:description>The actual conformance level of the Factur-X data</pdfaProperty:description>
                </rdf:li>
              </rdf:Seq>
            </pdfaSchema:property>
          </rdf:li>
        </rdf:Bag>
      </pdfaExtension:schemas>
    </rdf:Description>
"""

def _build_fx_xmp_description(filename: str, profile: str) -> str:
    # Standard profile names in XMP: MINIMUM, BASIC WL, BASIC, EN 16931, EXTENDED
    norm_profile = profile.replace("_", " ").upper()
    return f"""
    <rdf:Description xmlns:fx="urn:factur-x:pdfa:CrossIndustryDocument:invoice:1p0#"
                     rdf:about="">
      <fx:DocumentType>INVOICE</fx:DocumentType>
      <fx:DocumentFileName>{filename}</fx:DocumentFileName>
      <fx:Version>1.0</fx:Version>
      <fx:ConformanceLevel>{norm_profile}</fx:ConformanceLevel>
    </rdf:Description>
"""

def package_facturx_pdf(
    pdf_bytes: bytes,
    xml_bytes: bytes,
    profile: str = "EN 16931",
    filename: str = "factur-x.xml"
) -> bytes:
    """
    Embed factur-x.xml into a Typst-generated PDF/A-3b container.
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    writer = pypdf.PdfWriter()
    writer.append(reader)

    # 1. Update XMP Metadata
    now = datetime.datetime.now(datetime.timezone.utc)
    pdf_date_str = now.strftime("D:%Y%m%d%H%M%SZ")

    if "/Metadata" in reader.trailer["/Root"]:
        orig_meta_obj = reader.trailer["/Root"]["/Metadata"].get_object()
        orig_xmp_data = orig_meta_obj.get_data().decode("utf-8", errors="replace")
        
        # Inject extension schema and fx description before </rdf:RDF>
        if "urn:factur-x:pdfa:CrossIndustryDocument:invoice:1p0#" not in orig_xmp_data:
            injection = FACTURX_XMP_EXTENSION_SCHEMA + _build_fx_xmp_description(filename, profile)
            if "</rdf:RDF>" in orig_xmp_data:
                new_xmp_data = orig_xmp_data.replace("</rdf:RDF>", f"{injection}\n  </rdf:RDF>")
            else:
                new_xmp_data = orig_xmp_data + injection

            meta_stream = DecodedStreamObject()
            meta_stream.set_data(new_xmp_data.encode("utf-8"))
            meta_stream.update({
                NameObject("/Type"): NameObject("/Metadata"),
                NameObject("/Subtype"): NameObject("/XML"),
            })
            writer._root_object[NameObject("/Metadata")] = writer._add_object(meta_stream)

    # 2. Build EmbeddedFile Stream Object
    params = DictionaryObject({
        NameObject("/ModDate"): create_string_object(pdf_date_str),
        NameObject("/CreationDate"): create_string_object(pdf_date_str),
        NameObject("/Size"): pypdf.generic.NumberObject(len(xml_bytes)),
    })

    file_entry = DecodedStreamObject()
    file_entry.set_data(xml_bytes)
    file_entry.update({
        NameObject("/Type"): NameObject("/EmbeddedFile"),
        NameObject("/Subtype"): NameObject("/text#2Fxml"),
        NameObject("/Params"): params,
    })
    file_ref = writer._add_object(file_entry)

    # 3. Build File Specification Dictionary (/Filespec)
    filespec = DictionaryObject({
        NameObject("/Type"): NameObject("/Filespec"),
        NameObject("/F"): create_string_object(filename),
        NameObject("/UF"): create_string_object(filename),
        NameObject("/Desc"): create_string_object("Factur-X / ZUGFeRD electronic invoice"),
        NameObject("/AFRelationship"): NameObject("/Alternative"),
        NameObject("/EF"): DictionaryObject({
            NameObject("/F"): file_ref,
            NameObject("/UF"): file_ref,
        })
    })
    filespec_ref = writer._add_object(filespec)

    # 4. Attach to Document Catalog Names -> EmbeddedFiles
    if "/Names" not in writer._root_object:
        writer._root_object[NameObject("/Names")] = writer._add_object(DictionaryObject())
    names_dict = writer._root_object["/Names"].get_object()

    if "/EmbeddedFiles" not in names_dict:
        names_dict[NameObject("/EmbeddedFiles")] = writer._add_object(
            DictionaryObject({NameObject("/Names"): ArrayObject()})
        )
    ef_dict = names_dict["/EmbeddedFiles"].get_object()
    ef_names_array = ef_dict["/Names"]
    ef_names_array.extend([create_string_object(filename), filespec_ref])

    # 5. Attach to Document Catalog Associated Files (/AF)
    if "/AF" not in writer._root_object:
        writer._root_object[NameObject("/AF")] = writer._add_object(ArrayObject())
    af_array = writer._root_object["/AF"].get_object()
    af_array.append(filespec_ref)

    # 6. Write out packaged PDF
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()

def extract_facturx_xml(pdf_source: Union[bytes, str]) -> bytes:
    """
    Extract factur-x.xml / zugferd-invoice.xml from a PDF/A-3 container.
    """
    if isinstance(pdf_source, (str, bytes)) and isinstance(pdf_source, str):
        with open(pdf_source, "rb") as f:
            stream = io.BytesIO(f.read())
    else:
        stream = io.BytesIO(pdf_source)

    reader = pypdf.PdfReader(stream)

    # Method 1: reader.attachments
    target_names = ["factur-x.xml", "zugferd-invoice.xml", "xrechnung.xml"]
    for name in target_names:
        if name in reader.attachments:
            att = reader.attachments[name]
            if isinstance(att, list) and len(att) > 0:
                return bytes(att[0])
            return bytes(att)

    # Method 2: Inspect catalog /Names /EmbeddedFiles
    try:
        catalog = reader.trailer["/Root"]
        if "/Names" in catalog and "/EmbeddedFiles" in catalog["/Names"]:
            ef_dict = catalog["/Names"]["/EmbeddedFiles"].get_object()
            if "/Names" in ef_dict:
                names_arr = ef_dict["/Names"]
                for i in range(0, len(names_arr), 2):
                    entry_name = str(names_arr[i])
                    if any(t in entry_name.lower() for t in ("factur-x", "zugferd", "xrechnung", ".xml")):
                        filespec = names_arr[i + 1].get_object()
                        ef = filespec["/EF"].get_object()
                        stream_obj = (ef.get("/UF") or ef.get("/F")).get_object()
                        return stream_obj.get_data()
    except Exception:
        pass

    raise FileNotFoundError("No Factur-X or ZUGFeRD embedded XML found in PDF container.")
