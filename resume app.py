import streamlit as st
from io import BytesIO
from xhtml2pdf import pisa
from PyPDF2 import PdfReader
from docx import Document

st.set_page_config(page_title="Free Student Resume Builder", layout="wide")

# ------------------------ PDF UTILS ------------------------ #
def html_to_pdf(html: str) -> bytes | None:
    """Convert HTML string to PDF bytes using xhtml2pdf."""
    pdf_buffer = BytesIO()
    result = pisa.CreatePDF(html, dest=pdf_buffer)
    if result.err:
        return None
    return pdf_buffer.getvalue()


# ------------------------ RESUME PARSER ------------------------ #
def extract_text_from_pdf(file) -> str:
    reader = PdfReader(file)
    text = []
    for page in reader.pages:
        text.append(page.extract_text() or "")
    return "\n".join(text)


def extract_text_from_docx(file) -> str:
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)


def parse_uploaded_resume(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    else:
        return ""


# ------------------------ HTML TEMPLATES ------------------------ #
def render_template_1(data, page_style):
    """Simple classic ATS template."""
    page_css = """
        body { font-family: Arial, sans-serif; font-size: 11pt; color:#222; }
        .page { width: 800px; margin: 0 auto; padding: 24px 32px; }
    """
    if page_style == "Force 1 page (compact)":
        page_css += "body { font-size: 10pt; line-height: 1.1; }"
    elif page_style == "Allow multi-page":
        page_css += "@page { margin: 1.5cm; }"

    html = f"""
    <html>
    <head>
        <style>
            {page_css}
            h1, h2, h3 {{ margin: 0; padding: 0; }}
            h1 {{ font-size: 20pt; font-weight: bold; }}
            h2 {{ font-size: 12pt; margin-top: 12px; border-bottom: 1px solid #444; }}
            .section {{ margin-top: 10px; }}
            .header-contact {{ font-size: 9pt; margin-top: 4px; color:#555; }}
            .title-line {{ font-size: 11pt; font-weight: bold; margin-top: 4px; }}
            .item-title {{ font-weight:bold; }}
            .item-meta {{ font-style:italic; font-size: 9pt; color:#555; }}
            ul {{ margin-top: 4px; margin-bottom: 4px; padding-left: 18px; }}
        </style>
    </head>
    <body>
      <div class="page">
        <h1>{data['name']}</h1>
        <div class="header-contact">
          {data['email']} | {data['phone']} | {data['location']} | {data['linkedin']} {(" | " + data['github']) if data['github'] else ""}
        </div>
        <div class="title-line">{data['headline']}</div>

        <div class="section">
          <h2>SUMMARY</h2>
          <p>{data['summary']}</p>
        </div>

        <div class="section">
          <h2>EDUCATION</h2>
          """
    for edu in data["education"]:
        html += f"""
          <div>
            <span class="item-title">{edu['degree']} - {edu['school']}</span>
            <div class="item-meta">{edu['start_end']} | {edu['location']}</div>
            <div>{edu['details']}</div>
          </div>
        """
    html += """
        </div>

        <div class="section">
          <h2>EXPERIENCE</h2>
    """
    for exp in data["experience"]:
        html += f"""
          <div>
            <span class="item-title">{exp['role']} - {exp['company']}</span>
            <div class="item-meta">{exp['start_end']} | {exp['location']}</div>
            <ul>
        """
        for line in exp["bullets"].split("\n"):
            line = line.strip()
            if line:
                html += f"<li>{line}</li>"
        html += """
            </ul>
          </div>
        """
    html += """
        </div>

        <div class="section">
          <h2>PROJECTS</h2>
    """
    for proj in data["projects"]:
        html += f"""
          <div>
            <span class="item-title">{proj['name']}</span>
            <div class="item-meta">{proj['tech']}</div>
            <ul>
        """
        for line in proj["bullets"].split("\n"):
            line = line.strip()
            if line:
                html += f"<li>{line}</li>"
        html += """
            </ul>
          </div>
        """

    html += f"""
        </div>

        <div class="section">
          <h2>SKILLS</h2>
          <p><b>Technical:</b> {data['skills_technical']}</p>
          <p><b>Tools:</b> {data['skills_tools']}</p>
          <p><b>Soft Skills:</b> {data['skills_soft']}</p>
        </div>
      </div>
    </body>
    </html>
    """
    return html


def render_template_2(data, page_style):
    """Two-column ATS-safe template."""
    page_css = """
        body { font-family: Arial, sans-serif; font-size: 11pt; color:#222; }
        .page { width: 800px; margin: 0 auto; padding: 24px 32px; }
    """
    if page_style == "Force 1 page (compact)":
        page_css += "body { font-size: 10pt; line-height: 1.1; }"
    elif page_style == "Allow multi-page":
        page_css += "@page { margin: 1.5cm; }"

    html = f"""
    <html>
    <head>
      <style>
        {page_css}
        h1 {{ font-size: 20pt; margin-bottom: 4px; }}
        h2 {{ font-size: 12pt; margin-top: 10px; border-bottom: 1px solid #444; }}
        .header-contact {{ font-size: 9pt; color:#555; }}
        .layout {{ display: flex; gap: 16px; margin-top: 12px; }}
        .left-col {{ width: 32%; font-size: 10pt; }}
        .right-col {{ width: 68%; }}
        .section {{ margin-bottom: 10px; }}
        .item-title {{ font-weight:bold; }}
        .item-meta {{ font-style:italic; font-size: 9pt; color:#555; }}
        ul {{ margin-top: 4px; margin-bottom: 4px; padding-left: 18px; }}
      </style>
    </head>
    <body>
      <div class="page">
        <h1>{data['name']}</h1>
        <div class="header-contact">
          {data['email']} | {data['phone']} | {data['location']} | {data['linkedin']} {(" | " + data['github']) if data['github'] else ""}
        </div>
        <div class="layout">
          <div class="left-col">
            <div class="section">
              <h2>SUMMARY</h2>
              <p>{data['summary']}</p>
            </div>
            <div class="section">
              <h2>SKILLS</h2>
              <p><b>Technical:</b> {data['skills_technical']}</p>
              <p><b>Tools:</b> {data['skills_tools']}</p>
              <p><b>Soft:</b> {data['skills_soft']}</p>
            </div>
            <div class="section">
              <h2>LINKS</h2>
              <p>LinkedIn: {data['linkedin']}</p>
    """
    if data["github"]:
        html += f"<p>GitHub: {data['github']}</p>"

    html += """
            </div>
          </div>
          <div class="right-col">
            <div class="section">
              <h2>EDUCATION</h2>
    """
    for edu in data["education"]:
        html += f"""
              <div>
                <span class="item-title">{edu['degree']} - {edu['school']}</span>
                <div class="item-meta">{edu['start_end']} | {edu['location']}</div>
                <div>{edu['details']}</div>
              </div>
            """
    html += """
            </div>
            <div class="section">
              <h2>EXPERIENCE</h2>
    """
    for exp in data["experience"]:
        html += f"""
              <div>
                <span class="item-title">{exp['role']} - {exp['company']}</span>
                <div class="item-meta">{exp['start_end']} | {exp['location']}</div>
                <ul>
        """
        for line in exp["bullets"].split("\n"):
            line = line.strip()
            if line:
                html += f"<li>{line}</li>"
        html += """
                </ul>
              </div>
            """
    html += """
            </div>
            <div class="section">
              <h2>PROJECTS</h2>
    """
    for proj in data["projects"]:
        html += f"""
              <div>
                <span class="item-title">{proj['name']}</span>
                <div class="item-meta">{proj['tech']}</div>
                <ul>
        """
        for line in proj["bullets"].split("\n"):
            line = line.strip()
            if line:
                html += f"<li>{line}</li>"
        html += """
                </ul>
              </div>
            """

    html += """
            </div>
          </div>
        </div>
      </div>
    </body>
    </html>
    """
    return html


def render_template_3(data, page_style):
    """Variant with top bar and strong headings (still ATS-safe)."""
    page_css = """
        body { font-family: Arial, sans-serif; font-size: 11pt; color:#222; }
        .page { width: 800px; margin: 0 auto; padding: 0; }
    """
    if page_style == "Force 1 page (compact)":
        page_css += "body { font-size: 10pt; line-height: 1.1; }"
    elif page_style == "Allow multi-page":
        page_css += "@page { margin: 1.5cm; }"

    html = f"""
    <html>
    <head>
      <style>
        {page_css}
        .topbar {{
          background: #222;
          color: white;
          padding: 16px 28px;
        }}
        .topbar h1 {{ margin: 0; font-size: 20pt; }}
        .topbar .headline {{ font-size: 11pt; margin-top: 4px; }}
        .topbar .contact {{ font-size: 9pt; margin-top: 4px; color: #ddd; }}
        .content {{ padding: 18px 28px 24px 28px; }}
        h2 {{ font-size: 12pt; margin-top: 10px; border-bottom: 1px solid #444; }}
        .section {{ margin-bottom: 10px; }}
        .flex {{ display:flex; gap:24px; }}
        .half {{ width:50%; }}
        .item-title {{ font-weight:bold; }}
        .item-meta {{ font-style:italic; font-size: 9pt; color:#555; }}
        ul {{ margin-top: 4px; margin-bottom: 4px; padding-left: 18px; }}
      </style>
    </head>
    <body>
      <div class="page">
        <div class="topbar">
          <h1>{data['name']}</h1>
          <div class="headline">{data['headline']}</div>
          <div class="contact">
            {data['email']} | {data['phone']} | {data['location']} | {data['linkedin']} {(" | " + data['github']) if data['github'] else ""}
          </div>
        </div>
        <div class="content">
          <div class="section">
            <h2>SUMMARY</h2>
            <p>{data['summary']}</p>
          </div>

          <div class="flex">
            <div class="half">
              <div class="section">
                <h2>EDUCATION</h2>
    """
    for edu in data["education"]:
        html += f"""
                <div>
                  <span class="item-title">{edu['degree']} - {edu['school']}</span>
                  <div class="item-meta">{edu['start_end']} | {edu['location']}</div>
                  <div>{edu['details']}</div>
                </div>
              """
    html += """
              </div>
            </div>
            <div class="half">
              <div class="section">
                <h2>SKILLS</h2>
                <p><b>Technical:</b> {data['skills_technical']}</p>
                <p><b>Tools:</b> {data['skills_tools']}</p>
                <p><b>Soft Skills:</b> {data['skills_soft']}</p>
              </div>
            </div>
          </div>

          <div class="section">
            <h2>EXPERIENCE</h2>
    """
    for exp in data["experience"]:
        html += f"""
            <div>
              <span class="item-title">{exp['role']} - {exp['company']}</span>
              <div class="item-meta">{exp['start_end']} | {exp['location']}</div>
              <ul>
        """
        for line in exp["bullets"].split("\n"):
            line = line.strip()
            if line:
                html += f"<li>{line}</li>"
        html += """
              </ul>
            </div>
          """
    html += """
          </div>

          <div class="section">
            <h2>PROJECTS</h2>
    """
    for proj in data["projects"]:
        html += f"""
            <div>
              <span class="item-title">{proj['name']}</span>
              <div class="item-meta">{proj['tech']}</div>
              <ul>
        """
        for line in proj["bullets"].split("\n"):
            line = line.strip()
            if line:
                html += f"<li>{line}</li>"
        html += """
              </ul>
            </div>
          """
    html += """
          </div>
        </div>
      </div>
    </body>
    </html>
    """
    return html


def render_resume_html(data, template_name, page_style):
    if template_name == "Classic (Template 1)":
        return render_template_1(data, page_style)
    elif template_name == "Two-column (Template 2)":
        return render_template_2(data, page_style)
    else:
        return render_template_3(data, page_style)


# ------------------------ MAIN APP ------------------------ #
def main():
    st.title("🎓 Free Student Resume Builder (ATS Friendly)")
    st.write("No paywall. No account required. Your content stays as you type it – we only format it.")

    # ------------- CONFIG AREA (TEMPLATE + PAGES) ------------- #
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        template_name = st.selectbox(
            "Choose Resume Template",
            ["Classic (Template 1)", "Two-column (Template 2)", "Topbar (Template 3)"],
        )
    with col_cfg2:
        page_style = st.selectbox(
            "Page style preference",
            ["Automatic", "Force 1 page (compact)", "Allow multi-page"],
        )

    st.markdown("---")

    # ------------- UPLOAD OLD RESUME ------------- #
    st.subheader("1️⃣ Optional: Upload your existing resume (PDF/DOCX)")
    uploaded_resume = st.file_uploader("Upload file", type=["pdf", "docx"])
    extracted_text = ""
    if uploaded_resume is not None:
        extracted_text = parse_uploaded_resume(uploaded_resume)
        st.success("Resume text extracted. Use it as reference below.")
        st.text_area(
            "Extracted content (you can copy from here and paste into the sections below).",
            value=extracted_text,
            height=200,
        )

    st.markdown("---")

    # ------------- INPUT FORM ------------- #
    st.subheader("2️⃣ Fill your resume details (single long page)")

    # Basic info
    st.markdown("### Personal Details")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", value="")
        headline = st.text_input("Headline (e.g., B.Tech Student | Aspiring Data Analyst)")
        location = st.text_input("Location (City, Country)")
    with col2:
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        linkedin = st.text_input("LinkedIn URL")
        github = st.text_input("GitHub / Portfolio URL (optional)")

    summary = st.text_area(
        "Summary (2–4 lines about you, copy exactly what you want to appear)",
        height=120,
    )

    # Education
    st.markdown("### Education")
    num_edu = st.number_input(
        "How many education entries?", min_value=1, max_value=10, value=1, step=1
    )
    education = []
    for i in range(num_edu):
        st.markdown(f"**Education #{i+1}**")
        c1, c2 = st.columns(2)
        with c1:
            degree = st.text_input(f"Degree / Program #{i+1}")
            school = st.text_input(f"Institute / University #{i+1}")
        with c2:
            edu_dates = st.text_input(f"Duration #{i+1} (e.g., 2021 – Present)")
            edu_location = st.text_input(f"Location #{i+1}")
        details = st.text_area(
            f"Details / Highlights #{i+1} (CGPA, coursework, etc.)", height=80
        )
        education.append(
            {
                "degree": degree,
                "school": school,
                "start_end": edu_dates,
                "location": edu_location,
                "details": details,
            }
        )

    # Experience
    st.markdown("### Experience (Internships / Part-time / Volunteering)")
    num_exp = st.number_input(
        "How many experiences?", min_value=0, max_value=15, value=1, step=1
    )
    experience = []
    for i in range(num_exp):
        st.markdown(f"**Experience #{i+1}**")
        c1, c2 = st.columns(2)
        with c1:
            role = st.text_input(f"Role / Position #{i+1}")
            company = st.text_input(f"Company / Org #{i+1}")
        with c2:
            exp_dates = st.text_input(f"Duration #{i+1} (e.g., Jun 2024 – Aug 2024)")
            exp_location = st.text_input(f"Location #{i+1}")
        bullets = st.text_area(
            f"Bullet points #{i+1} (one line per bullet, exactly as you want)",
            height=100,
        )
        experience.append(
            {
                "role": role,
                "company": company,
                "start_end": exp_dates,
                "location": exp_location,
                "bullets": bullets,
            }
        )

    # Projects
    st.markdown("### Projects")
    num_projects = st.number_input(
        "How many projects?", min_value=0, max_value=15, value=2, step=1
    )
    projects = []
    for i in range(num_projects):
        st.markdown(f"**Project #{i+1}**")
        c1, c2 = st.columns(2)
        with c1:
            proj_name = st.text_input(f"Project Name #{i+1}")
        with c2:
            proj_tech = st.text_input(f"Tech/Tools Used #{i+1}")
        proj_bullets = st.text_area(
            f"Project details #{i+1} (one line per bullet, exactly as you want)",
            height=100,
        )
        projects.append(
            {
                "name": proj_name,
                "tech": proj_tech,
                "bullets": proj_bullets,
            }
        )

    # Skills
    st.markdown("### Skills")
    skills_technical = st.text_area(
        "Technical Skills (comma-separated, exactly as you want)",
        height=70,
    )
    skills_tools = st.text_area(
        "Tools / Platforms (comma-separated)", height=70
    )
    skills_soft = st.text_area(
        "Soft Skills (comma-separated)", height=70
    )

    # Collect all data
    resume_data = {
        "name": name,
        "headline": headline,
        "location": location,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "summary": summary,
        "education": education,
        "experience": experience,
        "projects": projects,
        "skills_technical": skills_technical,
        "skills_tools": skills_tools,
        "skills_soft": skills_soft,
    }

    st.markdown("---")

    # ------------- PREVIEW & DOWNLOAD ------------- #
    st.subheader("3️⃣ Preview & Download")

    if st.button("Generate Resume Preview"):
        html = render_resume_html(resume_data, template_name, page_style)
        st.session_state["resume_html"] = html
        st.success("Preview generated below.")

    if "resume_html" in st.session_state:
        st.markdown("#### Live HTML Preview (what your resume will look like)")
        st.components.v1.html(st.session_state["resume_html"], height=900, scrolling=True)

        if st.button("Generate PDF"):
            pdf_bytes = html_to_pdf(st.session_state["resume_html"])
            if pdf_bytes is None:
                st.error("PDF generation failed. Check xhtml2pdf installation.")
            else:
                st.download_button(
                    label="Download Resume as PDF",
                    data=pdf_bytes,
                    file_name="resume.pdf",
                    mime="application/pdf",
                )


if __name__ == "__main__":
    main()
