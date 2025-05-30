from bs4 import BeautifulSoup
import markdown

def visualize(self):
    html = BeautifulSoup(f'<html></html>', 'html.parser')

    head = html.new_tag("head")
    title = html.new_tag("title")
    title.string = f"Evaluation of page {self.page.p} of {self.page.doc.location}"
    head.append(title)
    html.html.append(head)

    style = html.new_tag("style", type="text/css")
    style.string = """
        @font-face {
            font-family: Helvetica;
            src: url(../../font/Helvetica.ttf);
        }
        html {
            font-family: "Helvetica";
        }   
        .columns {
            display: grid;
            grid-template-columns: 50% 50% 50%;
        }
        .columns > div {
            padding: 1rem;
            border-left: 1.5px solid rgba(0, 0, 0, 0.2);
            border-right: 1.5px solid rgba(0, 0, 0, 0.2);
        }"""

    html.html.append(style)

    body = html.new_tag("body")

    columns = html.new_tag("div")
    columns["class"] = "columns"

    div = html.new_tag("div")
    p = html.new_tag("p")

    colors = [["white","white"], 
              ["rgba(255, 255, 0, 0.6)", "rgba(255, 255, 0, 0.2)"], 
              ["rgba(255, 166, 0, 0.6)", "rgba(255, 166, 0, 0.2)"], 
              ["rgba(255, 0, 0, 0.6)", "rgba(255, 0, 0, 0.2)"], 
              ["rgba(139, 0, 0, 0.6)", "rgba(139, 0, 0, 0.2)"]]

    line = 0
    for token in self.ptt.tokens:
        if token.line != line:
            for i in range(token.line - line):
                p.append(html.new_tag("br"))
            line = token.line

        span = html.new_tag("span", style=f"background-color: {colors[token.missing][1 if token.border else 0]}")
        span.string = token.text
        p.append(span)

    div.append(p)
    columns.append(div)

    div = html.new_tag("div")

    md = self.page.md + "\n\n# HEADER\n" + self.page.header
    htmlmd = markdown.markdown(md, output_format='html')    

    soup = BeautifulSoup(htmlmd, 'html.parser')
    div.append(soup)

    columns.append(div)

    body.append(columns)
    html.html.append(body)

    with open(f"{self.page.doc.location.rstrip('.pdf')+f'_{self.page.p}.html'}", "w", encoding="utf-8") as file:
        file.write(html.prettify())
