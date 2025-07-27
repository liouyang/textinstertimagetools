from string import Template
import os
import markdown 

def generate_html_page(article_title: str, article_elements: list, output_filename: str = "generated_article.html", status_callback=None):
    if status_callback:
        status_callback.update(label=f"🌐 正在生成 HTML 页面: {output_filename}...", state="running")

    article_body_html = ""
    image_counter = 0 

    for item in article_elements:
        if item['type'] == 'paragraph':
            parsed_paragraph_content = markdown.markdown(item['content']).strip()
            if parsed_paragraph_content.startswith('<p>') and parsed_paragraph_content.endswith('</p>'):
                parsed_paragraph_content = parsed_paragraph_content[3:-4].strip()
            
            article_body_html += f"    <p>{parsed_paragraph_content}</p>\n"
            
        elif item['type'] == 'heading':
            parsed_heading_content = markdown.markdown(item['content']).strip()
            if parsed_heading_content.startswith('<p>') and parsed_heading_content.endswith('</p>'):
                parsed_heading_content = parsed_heading_content[3:-4].strip()

            article_body_html += f"    <h3>{parsed_heading_content}</h3>\n"
        
        elif item['type'] == 'image': 
            image_counter += 1 
            if 'base64_image_data' in item and item['base64_image_data']:
                article_body_html += f"""
    <div class="image-container">
        <img src="{item['base64_image_data']}" alt="文章配图 {image_counter}">
        <div class="image-caption">图 {image_counter}</div>
    </div>
""" 

    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_file_path = os.path.join(script_dir, "templates", "article_template.html")

    try:
        with open(template_file_path, "r", encoding="utf-8") as f:
            template_string = f.read()
    except FileNotFoundError:
        error_msg = f"❌ 错误: 模板文件 '{template_file_path}' 未找到。请确保它位于正确的位置。"
        if status_callback:
            status_callback.update(label=error_msg, state="error")
        print(error_msg)
        return
    
    template = Template(template_string)

    html_content = template.substitute(
        article_title=article_title,
        article_content=article_body_html
    )
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    if status_callback:
        status_callback.update(label=f"✅ HTML 页面已生成到: {output_filename}", state="running")