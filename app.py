import dash
from dash import html, dcc, Input, Output, State
import re
import PyPDF2

# Function to extract text from PDF starting from a specific page
def extract_text_from_pdf(pdf_path, start_page=11):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        text = ''
        for page_num in range(start_page, num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text

# Path to your PDF file
pdf_path = 'data/ConstitutionOfKenya.pdf'

# Extract constitution text directly from the PDF
constitution_text = extract_text_from_pdf(pdf_path)

# Function to extract all chapters and their content
def extract_all_chapters(constitution_text):
    chapters = []
    chapter_pattern = re.compile(r"CHAPTER\s+(\w+)\s*–\s*([^\n]+)?\b(.*?)(?=\nCHAPTER\s+\w+\b|\Z)", re.DOTALL)

    for match in chapter_pattern.finditer(constitution_text):
        chapter_number = match.group(1).strip()
        chapter_title = match.group(2).strip() if match.group(2) else "Unknown Title"
        chapter_content = match.group(3).strip()
        chapters.append({
            "chapter": chapter_number,
            "title": chapter_title,
            "content": chapter_content
        })

    return chapters

# Function to normalize text
def normalize_text(text):
    return ' '.join(text.lower().split())

# Function to extract articles from chapter content
def extract_articles(chapter_content):
    article_pattern = re.compile(r"(\d+)\.\s*(.*?)(?=\n\d+\.\s|\n\Z)", re.DOTALL)
    articles = []
    for match in article_pattern.finditer(chapter_content):
        article_number = match.group(1).strip()
        article_content = match.group(2).strip()
        articles.append({
            "article": article_number,
            "content": article_content
        })
    return articles

# Function to find a specific provision in the entire Constitution
def find_provision_in_constitution(constitution_text, provision_text):
    normalized_provision = normalize_text(provision_text)
    chapters = extract_all_chapters(constitution_text)
    results = []

    for chapter in chapters:
        articles = extract_articles(chapter["content"])
        for article in articles:
            normalized_article_content = normalize_text(article["content"])
            if normalized_provision in normalized_article_content:
                results.append({
                    "chapter": chapter["chapter"],
                    "title": chapter["title"],
                    "article": article["article"],
                    "content": article["content"]
                })

    return results

app = dash.Dash(__name__)

image_style = {
    "height": "200px",
    "width": "100%",
    "object-fit": "cover",
    "border-radius": "10px"
}

app.layout = html.Div([
    html.Div("📚 Kenyan Law", style={"text-align": "center", "color": "red", "font-size": "24px", "margin-top": "20px"}),
    html.H1("Welcome to Analyze the Constitution", style={"text-align": "center", "margin-bottom": "20px"}),
    dcc.Input(id="provision-input", placeholder="Enter a provision to search for...", style={"margin-bottom": "10px", "width": "100%", "padding": "10px"}),
    html.Button("Analyze", id="analyze-button", style={"background-color": "red", "color": "white", "padding": "10px 20px", "border": "none", "border-radius": "5px", "margin-bottom": "20px"}),
    html.Div(id="results-output", style={"margin-bottom": "20px"}),
    html.Div([
        html.Div([
            html.Img(src="/assets/Constitution.jpg", style=image_style),
            html.P("Analyze Constitutional Articles", style={"text-align": "center", "margin-top": "10px"})
        ], style={"flex": "1", "padding": "10px"}),
        html.Div([
            html.Img(src="/assets/hammer.jpg", style=image_style),
            html.P("Interpret Legal Provisions", style={"text-align": "center", "margin-top": "10px"})
        ], style={"flex": "1", "padding": "10px"}),
        html.Div([
            html.Img(src="/assets/logo.jpg", style=image_style),
            html.P("Explore Legal Precedents", style={"text-align": "center", "margin-top": "10px"})
        ], style={"flex": "1", "padding": "10px"})
    ], style={"display": "flex", "justify-content": "space-between"})
], style={"background-color": "lightgray", "padding": "40px", "border-radius": "10px"})

@app.callback(
    Output("results-output", "children"),
    Input("analyze-button", "n_clicks"),
    State("provision-input", "value"),
    prevent_initial_call=True
)
def analyze_provision(n_clicks, provision_text):
    if not provision_text:
        return "Please enter a provision to search for."

    results = find_provision_in_constitution(constitution_text, provision_text)

    if results:
        output = []
        for result in results:
            output.append(html.Div([
                html.H4(f"CHAPTER {result['chapter']} – {result['title']}"),
                html.P(f"Article {result['article']}"),
                html.P(result['content'])
            ], style={"margin-bottom": "20px"}))
        return output
    else:
        return "Provision not found in the Constitution."

if __name__ == '__main__':
    app.run_server(debug=True)
