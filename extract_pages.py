import argparse
from rich.console import Console
import pdfplumber
import os
import tiktoken

# Initialize Rich console for styled output
console = Console()


def count_tokens(text, model_name="o200k_base"):
    try:
        encoding = tiktoken.get_encoding(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")  # Fallback to 'cl100k_base'
        console.print(
            f"[warning]Model name '{model_name}' not found. Using 'cl100k_base' instead.[/warning]"
        )
    tokens = encoding.encode(text)
    return len(tokens)


def main():
    # Display welcome message
    console.print("[bold green]PDF Text Extractor[/bold green]")
    console.print(
        "This script extracts text from a specified range of pages in a PDF file.\n"
    )

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Extract text from a specified range of pages in a PDF file"
    )

    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("start_page", type=int, help="Start page number (1-indexed)")
    parser.add_argument("end_page", type=int, help="End page number (1-indexed)")

    args = parser.parse_args()

    pdf_path = args.pdf_path
    start_page = args.start_page
    end_page = args.end_page

    # Get and validate PDF file path
    if os.path.isfile(pdf_path) and pdf_path.lower().endswith(".pdf"):
        console.print("[green]Valid PDF file path.[/green]")
        pdf = pdfplumber.open(pdf_path)
    else:
        console.print(
            "[red]Invalid PDF file. Please enter a valid PDF file path.[/red]"
        )
        return

    # Extract text with a spinner for user feedback
    extracted_texts = []
    with console.status("Extracting text...", spinner="dots"):
        for i in range(start_page - 1, end_page):
            page = pdf.pages[i]
            text = (
                page.extract_text() or ""
            )  # Handle case where extract_text() returns None
            extracted_texts.append(text)
    extracted_text = "\n".join(extracted_texts)

    # Generate output filename by replacing the '.pdf' extension with '_<start_page>-<end_page>.txt'
    output_filename = pdf_path.replace(".pdf", f"_{start_page:03d}-{end_page:03d}.txt")

    # Save extracted text to file
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        console.print(f"[green]Text extracted and saved to {output_filename}[/green]")
    except Exception as e:
        console.print(f"[red]Error saving file: {e}[/red]")
    finally:
        pdf.close()

    # Count tokens in extracted text
    num_tokens = count_tokens(extracted_text)
    console.print(f"[bold]Number of tokens in extracted text:[/bold] {num_tokens}")
    console.print("[bold green]Done![/bold green]")


if __name__ == "__main__":
    main()
